from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Forbidden

from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.exceptions import (
    TestDriveNotFound,
    TestDriveStatusForbidden,
)
from modules.test_drives.domain.test_drive_messages import (
    TEST_DRIVE_EVENT_MAP,
    TEST_DRIVE_STATUS_LABELS,
)

from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType,
)

from modules.test_drives.application.dtos.update_test_drive_status_dto import (
    UpdateTestDriveStatusDTO,
)

from modules.test_drives.application.use_cases.update_test_drive_status import (
    UpdateTestDriveStatusUseCase,
)


# ============================================================
# HELPERS
# ============================================================


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
    brand="BMW",
    model="Serie 3",
):
    return SimpleNamespace(
        id=vehicle_id,
        brand=brand,
        model=model,
    )


def make_user(
    *,
    user_id="user-1",
    email="client@example.com",
):
    return SimpleNamespace(
        id=user_id,
        email=email,
    )


def make_test_drive(
    *,
    test_drive_id="test-drive-1",
    user_id="user-1",
    vehicle_id="vehicle-1",
    status=None,
    appointment_date=None,
    with_user=True,
    with_vehicle=True,
):
    if status is None:
        status = TestDriveStatus.PENDING

    if appointment_date is None:
        appointment_date = (
            datetime.now(timezone.utc)
            + timedelta(days=2)
        )

    vehicle = (
        make_vehicle(
            vehicle_id=vehicle_id,
        )
        if with_vehicle
        else None
    )

    user = (
        make_user(
            user_id=user_id,
        )
        if with_user
        else None
    )

    return SimpleNamespace(
        id=test_drive_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        status=status,
        appointment_date=appointment_date,
        vehicle=vehicle,
        user=user,
    )


def make_dto(
    *,
    test_drive_id="test-drive-1",
    actor_id="admin-1",
    actor_role=None,
    status=None,
):
    if actor_role is None:
        actor_role = UserRole.ADMIN

    if status is None:
        status = TestDriveStatus.CONFIRMED

    return UpdateTestDriveStatusDTO(
        test_drive_id=test_drive_id,
        actor_id=actor_id,
        actor_role=actor_role,
        status=status,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    repo = Mock()

    test_drive = make_test_drive()

    repo.get_full_by_id.return_value = test_drive

    # Le repository retourne l'objet réellement mis à jour.
    repo.update.side_effect = lambda test_drive: test_drive

    repo.count_pending.return_value = 3

    return repo


@pytest.fixture
def user_repository():
    repo = Mock()
    repo.get_by_role.return_value = []
    return repo


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def notification_service():
    service = Mock()
    service.send = AsyncMock()
    return service


@pytest.fixture
def websocket_manager():
    manager = Mock()
    manager.send = AsyncMock()
    return manager


@pytest.fixture
def use_case(
    repository,
    user_repository,
    event_service,
    unit_of_work,
    notification_service,
    websocket_manager,
):
    return UpdateTestDriveStatusUseCase(
        repository=repository,
        user_repository=user_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
        notification_service=notification_service,
        websocket_manager=websocket_manager,
    )


@pytest.fixture
def dto():
    return make_dto()


# ============================================================
# NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_test_drive_not_found(
    use_case,
    repository,
    unit_of_work,
    dto,
):
    repository.get_full_by_id.return_value = None

    with pytest.raises(TestDriveNotFound):
        await use_case.execute(dto)

    repository.get_full_by_id.assert_called_once_with(
        dto.test_drive_id
    )

    repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# CLIENT SECURITY
# ============================================================


@pytest.mark.asyncio
async def test_client_cannot_update_another_users_test_drive(
    use_case,
    repository,
    unit_of_work,
):
    test_drive = make_test_drive(
        user_id="owner-1"
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        actor_id="another-user",
        actor_role=UserRole.CLIENT,
        status=TestDriveStatus.CANCELLED,
    )

    with pytest.raises(Forbidden):
        await use_case.execute(dto)

    repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_client_can_cancel_own_test_drive(
    use_case,
    repository,
    unit_of_work,
):
    test_drive = make_test_drive(
        user_id="user-1"
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        actor_id="user-1",
        actor_role=UserRole.CLIENT,
        status=TestDriveStatus.CANCELLED,
    )

    result = await use_case.execute(dto)

    assert result is test_drive
    assert test_drive.status == TestDriveStatus.CANCELLED

    repository.update.assert_called_once_with(
        test_drive
    )

    unit_of_work.commit.assert_called_once()


@pytest.mark.asyncio
async def test_client_cannot_confirm_test_drive(
    use_case,
    repository,
    unit_of_work,
):
    test_drive = make_test_drive(
        user_id="user-1"
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        actor_id="user-1",
        actor_role=UserRole.CLIENT,
        status=TestDriveStatus.CONFIRMED,
    )

    with pytest.raises(TestDriveStatusForbidden):
        await use_case.execute(dto)

    repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_client_cannot_reject_test_drive(
    use_case,
    repository,
):
    test_drive = make_test_drive(
        user_id="user-1"
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        actor_id="user-1",
        actor_role=UserRole.CLIENT,
        status=TestDriveStatus.REJECTED,
    )

    with pytest.raises(TestDriveStatusForbidden):
        await use_case.execute(dto)

    repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_admin_can_update_test_drive_status(
    use_case,
    repository,
    unit_of_work,
):
    test_drive = make_test_drive()

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        actor_id="admin-1",
        actor_role=UserRole.ADMIN,
        status=TestDriveStatus.CONFIRMED,
    )

    result = await use_case.execute(dto)

    assert result is test_drive
    assert test_drive.status == TestDriveStatus.CONFIRMED

    repository.update.assert_called_once_with(
        test_drive
    )

    unit_of_work.commit.assert_called_once()


# ============================================================
# NO CHANGE
# ============================================================


@pytest.mark.asyncio
async def test_same_status_returns_test_drive_without_update(
    use_case,
    repository,
    event_service,
    unit_of_work,
    notification_service,
    websocket_manager,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.CONFIRMED
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED
    )

    result = await use_case.execute(dto)

    assert result is test_drive

    repository.update.assert_not_called()
    event_service.log.assert_not_called()

    notification_service.send.assert_not_awaited()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()

    websocket_manager.send.assert_not_awaited()


# ============================================================
# STATUS UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_status_is_updated(
    use_case,
    repository,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    result = await use_case.execute(dto)

    assert result is test_drive
    assert test_drive.status == dto.status


@pytest.mark.asyncio
async def test_repository_update_is_called(
    use_case,
    repository,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    await use_case.execute(dto)

    repository.update.assert_called_once_with(
        test_drive
    )


# ============================================================
# EVENT
# ============================================================


@pytest.mark.asyncio
async def test_event_is_logged_for_status_change(
    use_case,
    repository,
    event_service,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    await use_case.execute(dto)

    event_service.log.assert_called_once()

    event = event_service.log.call_args.kwargs

    expected_event_type = TEST_DRIVE_EVENT_MAP.get(
        dto.status
    )

    assert event["type"] == expected_event_type
    assert event["test_drive_id"] == test_drive.id
    assert event["vehicle_id"] == test_drive.vehicle_id
    assert event["user_id"] == dto.actor_id


@pytest.mark.asyncio
async def test_event_contains_old_and_new_status(
    use_case,
    repository,
    event_service,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    await use_case.execute(dto)

    event = event_service.log.call_args.kwargs

    assert event["event_metadata"]["customer_id"] == (
        test_drive.user_id
    )

    assert event["event_metadata"]["old_status"] == (
        TestDriveStatus.PENDING.value
    )

    assert event["event_metadata"]["new_status"] == (
        dto.status.value
    )


@pytest.mark.asyncio
async def test_event_message_contains_new_status_label(
    use_case,
    repository,
    event_service,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    await use_case.execute(dto)

    event = event_service.log.call_args.kwargs

    assert TEST_DRIVE_STATUS_LABELS[dto.status] in (
        event["message"]
    )


# ============================================================
# NOTIFICATION
# ============================================================


@pytest.mark.asyncio
async def test_notification_is_sent_when_user_exists(
    use_case,
    repository,
    notification_service,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING,
        with_user=True,
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED
    )

    await use_case.execute(dto)

    notification_service.send.assert_awaited_once()

    notification = (
        notification_service.send.await_args.kwargs
    )

    assert notification["user_id"] == test_drive.user_id
    assert notification["email"] == test_drive.user.email

    assert (
        notification["entity_type"]
        == NotificationEntityType.TEST_DRIVE
    )

    assert notification["entity_id"] == test_drive.id

    assert (
        notification["notif_type"]
        == NotificationType.TEST_DRIVE_CONFIRMED
    )


@pytest.mark.asyncio
async def test_no_notification_when_user_is_missing(
    use_case,
    repository,
    notification_service,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING,
        with_user=False,
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED
    )

    await use_case.execute(dto)

    notification_service.send.assert_not_awaited()


@pytest.mark.asyncio
async def test_notification_is_not_sent_when_notification_service_is_none(
    repository,
    user_repository,
    event_service,
    unit_of_work,
    websocket_manager,
):
    use_case = UpdateTestDriveStatusUseCase(
        repository=repository,
        user_repository=user_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
        notification_service=None,
        websocket_manager=websocket_manager,
    )

    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING,
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED
    )

    result = await use_case.execute(dto)

    assert result is test_drive
    unit_of_work.commit.assert_called_once()


# ============================================================
# NOTIFICATION BUILDER
# ============================================================


@pytest.mark.asyncio
async def test_confirmed_notification_content(
    use_case,
):
    test_drive = make_test_drive()

    notification = use_case._build_notification(
        TestDriveStatus.CONFIRMED,
        test_drive,
    )

    assert notification["title"] == (
        "Essai routier confirmé"
    )

    assert (
        notification["type"]
        == NotificationType.TEST_DRIVE_CONFIRMED
    )

    assert "BMW Serie 3" in notification["message"]
    assert "Bonjour" in notification["message"]


@pytest.mark.asyncio
async def test_rejected_notification_content(
    use_case,
):
    test_drive = make_test_drive()

    notification = use_case._build_notification(
        TestDriveStatus.REJECTED,
        test_drive,
    )

    assert notification["title"] == (
        "Essai routier refusé"
    )

    assert (
        notification["type"]
        == NotificationType.TEST_DRIVE_REJECTED
    )

    assert "BMW Serie 3" in notification["message"]


@pytest.mark.asyncio
async def test_cancelled_notification_content(
    use_case,
):
    test_drive = make_test_drive()

    notification = use_case._build_notification(
        TestDriveStatus.CANCELLED,
        test_drive,
    )

    assert notification["title"] == (
        "Essai routier annulé"
    )

    assert (
        notification["type"]
        == NotificationType.TEST_DRIVE_CANCELLED
    )

    assert "annulé" in notification["message"]


@pytest.mark.asyncio
async def test_completed_notification_content(
    use_case,
):
    test_drive = make_test_drive()

    notification = use_case._build_notification(
        TestDriveStatus.COMPLETED,
        test_drive,
    )

    assert notification["title"] == (
        "Essai routier terminé"
    )

    assert (
        notification["type"]
        == NotificationType.TEST_DRIVE_COMPLETED
    )

    assert "BMW Serie 3" in notification["message"]


def test_notification_uses_fallback_when_vehicle_is_missing(
    use_case,
):
    test_drive = make_test_drive(
        with_vehicle=False
    )

    notification = use_case._build_notification(
        TestDriveStatus.CONFIRMED,
        test_drive,
    )

    assert "véhicule non défini" in notification["message"]


def test_notification_uses_fallback_when_date_is_missing(
    use_case,
):
    test_drive = make_test_drive()

    test_drive.appointment_date = None

    notification = use_case._build_notification(
        TestDriveStatus.CONFIRMED,
        test_drive,
    )

    assert "date non définie" in notification["message"]


# ============================================================
# COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_commit_is_called(
    use_case,
    repository,
    unit_of_work,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# WEBSOCKET
# ============================================================


@pytest.mark.asyncio
async def test_admin_websocket_is_not_called_when_manager_is_none(
    repository,
    user_repository,
    event_service,
    unit_of_work,
    notification_service,
):
    use_case = UpdateTestDriveStatusUseCase(
        repository=repository,
        user_repository=user_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
        notification_service=notification_service,
        websocket_manager=None,
    )

    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED
    )

    result = await use_case.execute(dto)

    assert result is test_drive
    unit_of_work.commit.assert_called_once()


@pytest.mark.asyncio
async def test_admins_receive_pending_count_update(
    use_case,
    repository,
    user_repository,
    websocket_manager,
    dto,
):
    admins = [
        SimpleNamespace(id="admin-1"),
        SimpleNamespace(id="admin-2"),
    ]

    user_repository.get_by_role.return_value = admins
    repository.count_pending.return_value = 7

    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    await use_case.execute(dto)

    assert websocket_manager.send.await_count == 2

    websocket_manager.send.assert_any_await(
        "admin-1",
        {
            "type": "TEST_DRIVE_PENDING_UPDATED",
            "count": 7,
        },
    )

    websocket_manager.send.assert_any_await(
        "admin-2",
        {
            "type": "TEST_DRIVE_PENDING_UPDATED",
            "count": 7,
        },
    )


@pytest.mark.asyncio
async def test_pending_count_is_loaded_for_websocket(
    use_case,
    repository,
    user_repository,
    dto,
):
    user_repository.get_by_role.return_value = [
        SimpleNamespace(id="admin-1")
    ]

    repository.count_pending.return_value = 4

    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    await use_case.execute(dto)

    repository.count_pending.assert_called_once()

    user_repository.get_by_role.assert_called_once_with(
        UserRole.ADMIN
    )


@pytest.mark.asyncio
async def test_websocket_is_sent_after_commit(
    use_case,
    repository,
    user_repository,
    unit_of_work,
    websocket_manager,
    dto,
):
    user_repository.get_by_role.return_value = [
        SimpleNamespace(id="admin-1")
    ]

    repository.count_pending.return_value = 2

    order = []

    def commit():
        order.append("commit")

    unit_of_work.commit.side_effect = commit

    async def send_websocket(*args, **kwargs):
        order.append("websocket")

    websocket_manager.send.side_effect = send_websocket

    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    await use_case.execute(dto)

    assert order == [
        "commit",
        "websocket",
    ]


# ============================================================
# ROLLBACK / ERRORS
# ============================================================


@pytest.mark.asyncio
async def test_repository_update_error_rolls_back(
    use_case,
    repository,
    unit_of_work,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    repository.update.side_effect = RuntimeError(
        "update error"
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_event_error_rolls_back(
    use_case,
    repository,
    event_service,
    unit_of_work,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_notification_error_rolls_back(
    use_case,
    repository,
    notification_service,
    unit_of_work,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING,
        with_user=True,
    )

    repository.get_full_by_id.return_value = test_drive

    notification_service.send.side_effect = RuntimeError(
        "notification error"
    )

    with pytest.raises(
        RuntimeError,
        match="notification error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_commit_error_rolls_back(
    use_case,
    repository,
    unit_of_work,
    dto,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_error_rolls_back(
    use_case,
    repository,
    user_repository,
    websocket_manager,
    unit_of_work,
    dto,
):
    user_repository.get_by_role.return_value = [
        SimpleNamespace(id="admin-1")
    ]

    repository.count_pending.return_value = 2

    websocket_manager.send.side_effect = RuntimeError(
        "websocket error"
    )

    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    with pytest.raises(
        RuntimeError,
        match="websocket error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# COMPLETE FLOW
# ============================================================


@pytest.mark.asyncio
async def test_complete_status_update_flow(
    use_case,
    repository,
    user_repository,
    event_service,
    notification_service,
    unit_of_work,
    websocket_manager,
):
    test_drive = make_test_drive(
        test_drive_id="test-drive-42",
        user_id="customer-42",
        vehicle_id="vehicle-42",
        status=TestDriveStatus.PENDING,
    )

    repository.get_full_by_id.return_value = test_drive
    repository.count_pending.return_value = 5

    user_repository.get_by_role.return_value = [
        SimpleNamespace(id="admin-1")
    ]

    dto = make_dto(
        test_drive_id="test-drive-42",
        actor_id="admin-42",
        actor_role=UserRole.ADMIN,
        status=TestDriveStatus.CONFIRMED,
    )

    result = await use_case.execute(dto)

    # Load
    repository.get_full_by_id.assert_called_once_with(
        "test-drive-42"
    )

    # Status
    assert test_drive.status == (
        TestDriveStatus.CONFIRMED
    )

    # Repository
    repository.update.assert_called_once_with(
        test_drive
    )

    # Event
    event_service.log.assert_called_once()

    event = event_service.log.call_args.kwargs

    assert event["test_drive_id"] == "test-drive-42"
    assert event["vehicle_id"] == "vehicle-42"
    assert event["user_id"] == "admin-42"

    assert event["event_metadata"]["customer_id"] == (
        "customer-42"
    )

    assert event["event_metadata"]["old_status"] == (
        TestDriveStatus.PENDING.value
    )

    assert event["event_metadata"]["new_status"] == (
        TestDriveStatus.CONFIRMED.value
    )

    # Notification
    notification_service.send.assert_awaited_once()

    notification = (
        notification_service.send.await_args.kwargs
    )

    assert notification["user_id"] == "customer-42"
    assert notification["entity_id"] == "test-drive-42"

    # Commit
    unit_of_work.commit.assert_called_once()

    # WebSocket
    websocket_manager.send.assert_awaited_once_with(
        "admin-1",
        {
            "type": "TEST_DRIVE_PENDING_UPDATED",
            "count": 5,
        },
    )

    # Result
    assert result is test_drive