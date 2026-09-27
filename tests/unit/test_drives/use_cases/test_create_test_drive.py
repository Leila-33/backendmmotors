from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.exceptions import (
    TestDriveAlreadyExists,
    TestDrivePastDate,
    TestDriveSlotUnavailable,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleNotAvailableForTestDrive,
    VehicleNotFound,
)

from modules.applications.domain.enums import EventType
from modules.auth.domain.enums import UserRole
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType,
)

from modules.test_drives.application.use_cases.create_test_drive import (
    CreateTestDriveUseCase,
)


# ============================================================
# HELPERS
# ============================================================


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
    status=None,
):
    if status is None:
        status = VehicleStatus.PUBLISHED

    return SimpleNamespace(
        id=vehicle_id,
        status=status,
    )


def make_admin(
    *,
    admin_id="admin-1",
):
    return SimpleNamespace(
        id=admin_id,
        role=UserRole.ADMIN,
    )


def make_dto(
    *,
    vehicle_id="vehicle-1",
    appointment_date=None,
    comment="Je souhaite essayer ce véhicule.",
):
    if appointment_date is None:
        appointment_date = datetime.now(timezone.utc) + timedelta(days=1)

    return SimpleNamespace(
        vehicle_id=vehicle_id,
        appointment_date=appointment_date,
        comment=comment,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def user_repository():
    repository = Mock()
    repository.get_by_role.return_value = []
    return repository


@pytest.fixture
def test_drive_repository():
    repository = Mock()

    repository.has_existing_blocking_test_drive.return_value = False
    repository.find_conflicting_slot.return_value = None
    repository.count_pending.return_value = 1

    return repository


@pytest.fixture
def vehicle_repository():
    repository = Mock()
    repository.get_by_id.return_value = make_vehicle()
    return repository


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def notification_service():
    service = Mock()
    service.send = AsyncMock()
    return service


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def websocket_manager():
    manager = Mock()
    manager.send = AsyncMock()
    return manager


@pytest.fixture
def use_case(
    user_repository,
    test_drive_repository,
    vehicle_repository,
    event_service,
    notification_service,
    unit_of_work,
    websocket_manager,
):
    return CreateTestDriveUseCase(
        user_repository=user_repository,
        test_drive_repository=test_drive_repository,
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        notification_service=notification_service,
        unit_of_work=unit_of_work,
        websocket_manager=websocket_manager,
    )


@pytest.fixture
def dto():
    return make_dto()


@pytest.fixture
def user_id():
    return "user-1"


# ============================================================
# VEHICLE
# ============================================================


def test_vehicle_not_found(
    use_case,
    vehicle_repository,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        import asyncio

        asyncio.run(
            use_case.execute(
                dto=dto,
                user_id=user_id,
            )
        )

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_vehicle_not_found_async(
    use_case,
    vehicle_repository,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_vehicle_not_available_for_test_drive(
    use_case,
    vehicle_repository,
    unit_of_work,
    dto,
    user_id,
):
    non_published_statuses = [
        status
        for status in VehicleStatus
        if status != VehicleStatus.PUBLISHED
    ]

    if not non_published_statuses:
        pytest.skip(
            "VehicleStatus ne contient pas d'autre statut que PUBLISHED."
        )

    vehicle_repository.get_by_id.return_value = make_vehicle(
        status=non_published_statuses[0]
    )

    import asyncio

    with pytest.raises(VehicleNotAvailableForTestDrive):
        asyncio.run(
            use_case.execute(
                dto=dto,
                user_id=user_id,
            )
        )

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# EXISTING TEST DRIVE
# ============================================================


@pytest.mark.asyncio
async def test_existing_blocking_test_drive_is_rejected(
    use_case,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    test_drive_repository.has_existing_blocking_test_drive.return_value = True

    with pytest.raises(TestDriveAlreadyExists):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    test_drive_repository.has_existing_blocking_test_drive.assert_called_once_with(
        user_id=user_id,
        vehicle_id=dto.vehicle_id,
    )

    test_drive_repository.find_conflicting_slot.assert_not_called()
    test_drive_repository.create.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# DATE
# ============================================================


@pytest.mark.asyncio
async def test_past_appointment_date_is_rejected(
    use_case,
    dto,
    user_id,
    unit_of_work,
):
    dto.appointment_date = (
        datetime.now(timezone.utc) - timedelta(minutes=1)
    )

    with pytest.raises(TestDrivePastDate):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_current_appointment_date_is_rejected(
    use_case,
    dto,
    user_id,
    unit_of_work,
):
    dto.appointment_date = datetime.now(timezone.utc)

    with pytest.raises(TestDrivePastDate):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# SLOT
# ============================================================


@pytest.mark.asyncio
async def test_conflicting_slot_is_rejected(
    use_case,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    test_drive_repository.find_conflicting_slot.return_value = (
        SimpleNamespace(id="existing-test-drive")
    )

    with pytest.raises(TestDriveSlotUnavailable):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    test_drive_repository.find_conflicting_slot.assert_called_once_with(
        vehicle_id=dto.vehicle_id,
        appointment_date=dto.appointment_date,
    )

    test_drive_repository.create.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# CREATE
# ============================================================


@pytest.mark.asyncio
async def test_test_drive_is_created(
    use_case,
    test_drive_repository,
    dto,
    user_id,
):
    result = await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    test_drive_repository.create.assert_called_once()

    created_test_drive = (
        test_drive_repository.create.call_args.args[0]
    )

    assert isinstance(
        created_test_drive,
        TestDrive,
    )

    assert created_test_drive.user_id == user_id
    assert created_test_drive.vehicle_id == dto.vehicle_id
    assert (
        created_test_drive.appointment_date
        == dto.appointment_date
    )
    assert created_test_drive.comment == dto.comment
    assert created_test_drive.status == TestDriveStatus.PENDING


@pytest.mark.asyncio
async def test_created_test_drive_has_an_id(
    use_case,
    test_drive_repository,
    dto,
    user_id,
):
    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    created_test_drive = (
        test_drive_repository.create.call_args.args[0]
    )

    assert created_test_drive.id
    assert isinstance(
        created_test_drive.id,
        str,
    )


@pytest.mark.asyncio
async def test_created_test_drive_has_created_at(
    use_case,
    test_drive_repository,
    dto,
    user_id,
):
    before = datetime.now(timezone.utc)

    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    after = datetime.now(timezone.utc)

    created_test_drive = (
        test_drive_repository.create.call_args.args[0]
    )

    assert created_test_drive.created_at is not None
    assert before <= created_test_drive.created_at <= after


# ============================================================
# EVENT
# ============================================================


@pytest.mark.asyncio
async def test_test_drive_created_event_is_logged(
    use_case,
    event_service,
    dto,
    user_id,
    vehicle_repository,
):
    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    event_service.log.assert_called_once()

    call = event_service.log.call_args

    assert call.kwargs["type"] == EventType.TEST_DRIVE_CREATED
    assert call.kwargs["message"] == (
        "Demande d'essai véhicule créée"
    )
    assert call.kwargs["user_id"] == user_id
    assert call.kwargs["vehicle_id"] == (
        vehicle_repository.get_by_id.return_value.id
    )

    assert "test_drive_id" in call.kwargs
    assert "event_metadata" in call.kwargs


@pytest.mark.asyncio
async def test_event_contains_test_drive_information(
    use_case,
    event_service,
    test_drive_repository,
    dto,
    user_id,
):
    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    created_test_drive = (
        test_drive_repository.create.call_args.args[0]
    )

    event = event_service.log.call_args.kwargs

    assert event["test_drive_id"] == created_test_drive.id

    assert event["event_metadata"]["appointment_date"] == (
        dto.appointment_date.isoformat()
    )

    assert event["event_metadata"]["status"] == (
        TestDriveStatus.PENDING.value
    )


# ============================================================
# ADMIN NOTIFICATIONS
# ============================================================


@pytest.mark.asyncio
async def test_admins_are_loaded(
    use_case,
    user_repository,
    dto,
    user_id,
):
    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    user_repository.get_by_role.assert_called_once_with(
        UserRole.ADMIN
    )


@pytest.mark.asyncio
async def test_each_admin_receives_notification(
    use_case,
    user_repository,
    notification_service,
    dto,
    user_id,
):
    admins = [
        make_admin(admin_id="admin-1"),
        make_admin(admin_id="admin-2"),
        make_admin(admin_id="admin-3"),
    ]

    user_repository.get_by_role.return_value = admins

    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert notification_service.send.await_count == 3

    notification_service.send.assert_any_await(
        user_id="admin-1",
        title="Nouvel essai routier",
        message=(
            "Un client a demandé un essai routier."
        ),
        notif_type=NotificationType.TEST_DRIVE_CREATED,
        entity_type=NotificationEntityType.TEST_DRIVE,
        entity_id=(
            notification_service.send.await_args_list[0]
            .kwargs["entity_id"]
        ),
    )


@pytest.mark.asyncio
async def test_no_notification_is_sent_when_there_are_no_admins(
    use_case,
    user_repository,
    notification_service,
    dto,
    user_id,
):
    user_repository.get_by_role.return_value = []

    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    notification_service.send.assert_not_awaited()


# ============================================================
# COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_unit_of_work_is_committed(
    use_case,
    unit_of_work,
    dto,
    user_id,
):
    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# PENDING COUNT
# ============================================================


@pytest.mark.asyncio
async def test_pending_count_is_loaded_after_commit(
    use_case,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    test_drive_repository.count_pending.return_value = 7

    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    unit_of_work.commit.assert_called_once()

    test_drive_repository.count_pending.assert_called_once()


# ============================================================
# WEBSOCKET
# ============================================================


@pytest.mark.asyncio
async def test_each_admin_receives_websocket_update(
    use_case,
    user_repository,
    websocket_manager,
    test_drive_repository,
    dto,
    user_id,
):
    admins = [
        make_admin(admin_id="admin-1"),
        make_admin(admin_id="admin-2"),
    ]

    user_repository.get_by_role.return_value = admins
    test_drive_repository.count_pending.return_value = 5

    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert websocket_manager.send.await_count == 2

    websocket_manager.send.assert_any_await(
        "admin-1",
        {
            "type": "TEST_DRIVE_PENDING_UPDATED",
            "count": 5,
        },
    )

    websocket_manager.send.assert_any_await(
        "admin-2",
        {
            "type": "TEST_DRIVE_PENDING_UPDATED",
            "count": 5,
        },
    )


@pytest.mark.asyncio
async def test_websocket_update_is_sent_after_commit(
    use_case,
    user_repository,
    unit_of_work,
    websocket_manager,
    dto,
    user_id,
):
    user_repository.get_by_role.return_value = [
        make_admin(admin_id="admin-1")
    ]

    order = []

    def commit():
        order.append("commit")

    unit_of_work.commit.side_effect = commit

    async def send_websocket(*args, **kwargs):
        order.append("websocket")

    websocket_manager.send.side_effect = send_websocket

    await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert order == [
        "commit",
        "websocket",
    ]

    unit_of_work.commit.assert_called_once()

    websocket_manager.send.assert_awaited_once_with(
        "admin-1",
        {
            "type": "TEST_DRIVE_PENDING_UPDATED",
            "count": 1,
        },
    )

# ============================================================
# RESULT
# ============================================================


@pytest.mark.asyncio
async def test_created_test_drive_is_returned(
    use_case,
    test_drive_repository,
    dto,
    user_id,
):
    result = await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    created_test_drive = (
        test_drive_repository.create.call_args.args[0]
    )

    assert result is created_test_drive


@pytest.mark.asyncio
async def test_result_is_test_drive(
    use_case,
    dto,
    user_id,
):
    result = await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    assert isinstance(
        result,
        TestDrive,
    )


# ============================================================
# ROLLBACK / ERRORS
# ============================================================


@pytest.mark.asyncio
async def test_vehicle_repository_error_rolls_back(
    use_case,
    vehicle_repository,
    unit_of_work,
    dto,
    user_id,
):
    vehicle_repository.get_by_id.side_effect = RuntimeError(
        "vehicle repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="vehicle repository error",
    ):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_existing_test_drive_check_error_rolls_back(
    use_case,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    test_drive_repository.has_existing_blocking_test_drive.side_effect = (
        RuntimeError("existing test drive error")
    )

    with pytest.raises(
        RuntimeError,
        match="existing test drive error",
    ):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_slot_check_error_rolls_back(
    use_case,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    test_drive_repository.find_conflicting_slot.side_effect = (
        RuntimeError("slot error")
    )

    with pytest.raises(
        RuntimeError,
        match="slot error",
    ):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_error_rolls_back(
    use_case,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    test_drive_repository.create.side_effect = RuntimeError(
        "create error"
    )

    with pytest.raises(
        RuntimeError,
        match="create error",
    ):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_event_error_rolls_back(
    use_case,
    event_service,
    unit_of_work,
    dto,
    user_id,
):
    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_notification_error_rolls_back(
    use_case,
    user_repository,
    notification_service,
    unit_of_work,
    dto,
    user_id,
):
    user_repository.get_by_role.return_value = [
        make_admin()
    ]

    notification_service.send.side_effect = RuntimeError(
        "notification error"
    )

    with pytest.raises(
        RuntimeError,
        match="notification error",
    ):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_commit_error_rolls_back(
    use_case,
    unit_of_work,
    dto,
    user_id,
):
    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_pending_count_error_rolls_back(
    use_case,
    test_drive_repository,
    unit_of_work,
    dto,
    user_id,
):
    test_drive_repository.count_pending.side_effect = (
        RuntimeError("count error")
    )

    with pytest.raises(
        RuntimeError,
        match="count error",
    ):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_error_rolls_back(
    use_case,
    user_repository,
    websocket_manager,
    unit_of_work,
    dto,
    user_id,
):
    user_repository.get_by_role.return_value = [
        make_admin()
    ]

    websocket_manager.send.side_effect = RuntimeError(
        "websocket error"
    )

    with pytest.raises(
        RuntimeError,
        match="websocket error",
    ):
        await use_case.execute(
            dto=dto,
            user_id=user_id,
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# COMPLETE FLOW
# ============================================================


@pytest.mark.asyncio
async def test_complete_creation_flow(
    use_case,
    user_repository,
    vehicle_repository,
    test_drive_repository,
    event_service,
    notification_service,
    unit_of_work,
    websocket_manager,
    dto,
    user_id,
):
    admin = make_admin(admin_id="admin-42")

    user_repository.get_by_role.return_value = [
        admin
    ]

    test_drive_repository.count_pending.return_value = 4

    result = await use_case.execute(
        dto=dto,
        user_id=user_id,
    )

    # Vehicle
    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    # Existing test drive
    test_drive_repository.has_existing_blocking_test_drive.assert_called_once_with(
        user_id=user_id,
        vehicle_id=dto.vehicle_id,
    )

    # Slot
    test_drive_repository.find_conflicting_slot.assert_called_once_with(
        vehicle_id=dto.vehicle_id,
        appointment_date=dto.appointment_date,
    )

    # Creation
    test_drive_repository.create.assert_called_once()

    created_test_drive = (
        test_drive_repository.create.call_args.args[0]
    )

    assert created_test_drive.user_id == user_id
    assert created_test_drive.vehicle_id == dto.vehicle_id
    assert created_test_drive.status == TestDriveStatus.PENDING

    # Event
    event_service.log.assert_called_once()

    # Notification
    notification_service.send.assert_awaited_once()

    # Commit
    unit_of_work.commit.assert_called_once()

    # Count
    test_drive_repository.count_pending.assert_called_once()

    # Websocket
    websocket_manager.send.assert_awaited_once_with(
        "admin-42",
        {
            "type": "TEST_DRIVE_PENDING_UPDATED",
            "count": 4,
        },
    )

    # Result
    assert result is created_test_drive