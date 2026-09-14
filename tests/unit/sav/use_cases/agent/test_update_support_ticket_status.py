from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Forbidden
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
from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.exceptions import (
    TestDriveNotFound,
    TestDriveStatusForbidden,
)


# ============================================================
# HELPERS
# ============================================================


def make_test_drive(
    *,
    test_drive_id="test-drive-1",
    user_id="user-1",
    vehicle_id="vehicle-1",
    appointment_date=datetime(2026, 9, 15, 14, 30),
    status=TestDriveStatus.PENDING,
    user=None,
    vehicle=None,
):
    return TestDrive(
        id=test_drive_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        appointment_date=appointment_date,
        status=status,
        comment=None,
        created_at=datetime(2026, 9, 1, 10, 0),
        user=user,
        vehicle=vehicle,
    )


def make_user():
    return Mock(
        id="user-1",
        email="client@example.com",
    )


def make_vehicle():
    return Mock(
        brand="BMW",
        model="Série 3",
    )


def make_dto(
    *,
    test_drive_id="test-drive-1",
    status=TestDriveStatus.CONFIRMED,
    actor_id="user-1",
    actor_role=UserRole.CLIENT,
):
    return UpdateTestDriveStatusDTO(
        test_drive_id=test_drive_id,
        status=status,
        actor_id=actor_id,
        actor_role=actor_role,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def notification_service():
    service = Mock()
    service.send = AsyncMock()
    return service


@pytest.fixture
def uow():
    return Mock()


@pytest.fixture
def use_case(
    repository,
    event_service,
    notification_service,
    uow,
):
    return UpdateTestDriveStatusUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=uow,
        notification_service=notification_service,
    )


# ============================================================
# NOT FOUND
# ============================================================


def test_test_drive_not_found(
    use_case,
    repository,
    uow,
):
    repository.get_full_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(TestDriveNotFound):
        import asyncio

        asyncio.run(
            use_case.execute(dto)
        )

    repository.get_full_by_id.assert_called_once_with(
        "test-drive-1"
    )

    uow.rollback.assert_not_called()
    uow.commit.assert_not_called()


# ============================================================
# SECURITY — CLIENT
# ============================================================


def test_client_cannot_update_another_users_test_drive(
    use_case,
    repository,
    uow,
):
    test_drive = make_test_drive(
        user_id="owner-1"
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        actor_id="another-user",
        status=TestDriveStatus.CANCELLED,
        actor_role=UserRole.CLIENT,
    )

    with pytest.raises(Forbidden):
        import asyncio

        asyncio.run(
            use_case.execute(dto)
        )

    repository.update.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


@pytest.mark.parametrize(
    "status",
    [
        TestDriveStatus.PENDING,
        TestDriveStatus.CONFIRMED,
        TestDriveStatus.REJECTED,
        TestDriveStatus.COMPLETED,
    ],
)
def test_client_can_only_cancel_test_drive(
    status,
    use_case,
    repository,
    uow,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        status=status,
        actor_role=UserRole.CLIENT,
        actor_id="user-1",
    )

    with pytest.raises(TestDriveStatusForbidden):
        import asyncio

        asyncio.run(
            use_case.execute(dto)
        )

    repository.update.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


def test_client_can_cancel_own_test_drive(
    use_case,
    repository,
    uow,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CANCELLED,
        actor_id="user-1",
        actor_role=UserRole.CLIENT,
    )

    import asyncio

    result = asyncio.run(
        use_case.execute(dto)
    )

    assert result is test_drive
    assert test_drive.status == TestDriveStatus.CANCELLED

    repository.update.assert_called_once_with(
        test_drive
    )

    uow.commit.assert_called_once()


# ============================================================
# NO CHANGE
# ============================================================


def test_returns_without_updating_when_status_is_unchanged(
    use_case,
    repository,
    event_service,
    notification_service,
    uow,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.CONFIRMED
    )

    repository.get_full_by_id.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    import asyncio

    result = asyncio.run(
        use_case.execute(dto)
    )

    assert result is test_drive

    repository.update.assert_not_called()
    event_service.log.assert_not_called()
    notification_service.send.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


# ============================================================
# UPDATE STATUS
# ============================================================


@pytest.mark.parametrize(
    "new_status",
    [
        TestDriveStatus.CONFIRMED,
        TestDriveStatus.REJECTED,
        TestDriveStatus.CANCELLED,
        TestDriveStatus.COMPLETED,
    ],
)
def test_status_is_updated(
    new_status,
    use_case,
    repository,
    uow,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    dto = make_dto(
        status=new_status,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    import asyncio

    result = asyncio.run(
        use_case.execute(dto)
    )

    assert result is test_drive
    assert test_drive.status == new_status

    repository.update.assert_called_once_with(
        test_drive
    )

    uow.commit.assert_called_once()


def test_repository_updated_test_drive_is_used(
    use_case,
    repository,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    updated_test_drive = make_test_drive(
        status=TestDriveStatus.CONFIRMED
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = updated_test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    import asyncio

    result = asyncio.run(
        use_case.execute(dto)
    )

    # Le use case retourne actuellement test_drive
    # et non updated_test_drive.
    assert result is test_drive

    repository.update.assert_called_once_with(
        test_drive
    )


# ============================================================
# EVENTS
# ============================================================


@pytest.mark.parametrize(
    "status",
    [
        TestDriveStatus.CONFIRMED,
        TestDriveStatus.REJECTED,
        TestDriveStatus.CANCELLED,
        TestDriveStatus.COMPLETED,
    ],
)
def test_event_is_logged(
    status,
    use_case,
    repository,
    event_service,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    dto = make_dto(
        status=status,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    import asyncio

    asyncio.run(
        use_case.execute(dto)
    )

    event_service.log.assert_called_once()

    call_kwargs = (
        event_service.log.call_args.kwargs
    )

    assert call_kwargs["test_drive_id"] == (
        "test-drive-1"
    )

    assert call_kwargs["vehicle_id"] == (
        "vehicle-1"
    )

    assert call_kwargs["user_id"] == (
        "agent-1"
    )

    assert call_kwargs["event_metadata"] == {
        "customer_id": "user-1",
        "old_status": "pending",
        "new_status": status.value,
    }


def test_event_message_contains_new_status_label(
    use_case,
    repository,
    event_service,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    import asyncio

    asyncio.run(
        use_case.execute(dto)
    )

    message = (
        event_service.log.call_args.kwargs[
            "message"
        ]
    )

    assert message == (
        "Statut de l'essai routier changé vers "
        "Confirmé"
    )


# ============================================================
# NOTIFICATIONS
# ============================================================


@pytest.mark.parametrize(
    "status, notification_type, title",
    [
        (
            TestDriveStatus.CONFIRMED,
            NotificationType.TEST_DRIVE_CONFIRMED,
            "Essai routier confirmé",
        ),
        (
            TestDriveStatus.REJECTED,
            NotificationType.TEST_DRIVE_REJECTED,
            "Essai routier refusé",
        ),
        (
            TestDriveStatus.CANCELLED,
            NotificationType.TEST_DRIVE_CANCELLED,
            "Essai routier annulé",
        ),
        (
            TestDriveStatus.COMPLETED,
            NotificationType.TEST_DRIVE_COMPLETED,
            "Essai routier terminé",
        ),
    ],
)
def test_notification_is_sent(
    status,
    notification_type,
    title,
    use_case,
    repository,
    notification_service,
):
    user = make_user()
    vehicle = make_vehicle()

    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING,
        user=user,
        vehicle=vehicle,
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    dto = make_dto(
        status=status,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    import asyncio

    asyncio.run(
        use_case.execute(dto)
    )

    notification_service.send.assert_called_once()

    call_kwargs = (
        notification_service.send.call_args.kwargs
    )

    assert call_kwargs["user_id"] == "user-1"

    assert call_kwargs["email"] == (
        "client@example.com"
    )

    assert call_kwargs["entity_type"] == (
        NotificationEntityType.TEST_DRIVE
    )

    assert call_kwargs["entity_id"] == (
        "test-drive-1"
    )

    assert call_kwargs["title"] == title

    assert call_kwargs["notif_type"] == (
        notification_type
    )


def test_no_notification_service_means_no_notification(
    repository,
    event_service,
    uow,
):
    use_case = UpdateTestDriveStatusUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=uow,
        notification_service=None,
    )

    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    import asyncio

    result = asyncio.run(
        use_case.execute(dto)
    )

    assert result is test_drive
    uow.commit.assert_called_once()


def test_no_notification_when_user_is_missing(
    use_case,
    repository,
    notification_service,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING,
        user=None,
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    import asyncio

    asyncio.run(
        use_case.execute(dto)
    )

    notification_service.send.assert_not_called()


# ============================================================
# BUILD NOTIFICATION
# ============================================================


@pytest.mark.parametrize(
    "status, expected_type, expected_title",
    [
        (
            TestDriveStatus.CONFIRMED,
            NotificationType.TEST_DRIVE_CONFIRMED,
            "Essai routier confirmé",
        ),
        (
            TestDriveStatus.REJECTED,
            NotificationType.TEST_DRIVE_REJECTED,
            "Essai routier refusé",
        ),
        (
            TestDriveStatus.CANCELLED,
            NotificationType.TEST_DRIVE_CANCELLED,
            "Essai routier annulé",
        ),
        (
            TestDriveStatus.COMPLETED,
            NotificationType.TEST_DRIVE_COMPLETED,
            "Essai routier terminé",
        ),
    ],
)
def test_build_notification(
    use_case,
    status,
    expected_type,
    expected_title,
):
    test_drive = make_test_drive(
        user=make_user(),
        vehicle=make_vehicle(),
    )

    result = use_case._build_notification(
        status,
        test_drive,
    )

    assert result["type"] == expected_type
    assert result["title"] == expected_title

    assert "15/09/2026 à 14:30" in (
        result["message"]
    )


def test_build_cancelled_notification_does_not_require_vehicle(
    use_case,
):
    test_drive = make_test_drive(
        vehicle=None
    )

    result = use_case._build_notification(
        TestDriveStatus.CANCELLED,
        test_drive,
    )

    assert result["type"] == (
        NotificationType.TEST_DRIVE_CANCELLED
    )

    assert "15/09/2026 à 14:30" in (
        result["message"]
    )


# ============================================================
# ROLLBACK — ERRORS
# ============================================================


def test_repository_update_error_rolls_back(
    use_case,
    repository,
    uow,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive

    repository.update.side_effect = RuntimeError(
        "update error"
    )

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        import asyncio

        asyncio.run(
            use_case.execute(dto)
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_event_error_rolls_back(
    use_case,
    repository,
    event_service,
    uow,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        import asyncio

        asyncio.run(
            use_case.execute(dto)
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_notification_error_rolls_back(
    use_case,
    repository,
    notification_service,
    uow,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING,
        user=make_user(),
        vehicle=make_vehicle(),
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    notification_service.send.side_effect = (
        RuntimeError("notification error")
    )

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    with pytest.raises(
        RuntimeError,
        match="notification error",
    ):
        import asyncio

        asyncio.run(
            use_case.execute(dto)
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_commit_error_rolls_back(
    use_case,
    repository,
    uow,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    uow.commit.side_effect = RuntimeError(
        "commit error"
    )

    dto = make_dto(
        status=TestDriveStatus.CONFIRMED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        import asyncio

        asyncio.run(
            use_case.execute(dto)
        )

    uow.commit.assert_called_once()
    uow.rollback.assert_called_once()


# ============================================================
# FINAL RESULT
# ============================================================


def test_returns_updated_test_drive(
    use_case,
    repository,
):
    test_drive = make_test_drive(
        status=TestDriveStatus.PENDING
    )

    repository.get_full_by_id.return_value = test_drive
    repository.update.return_value = test_drive

    dto = make_dto(
        status=TestDriveStatus.COMPLETED,
        actor_id="agent-1",
        actor_role=UserRole.ADMIN,
    )

    import asyncio

    result = asyncio.run(
        use_case.execute(dto)
    )

    assert isinstance(result, TestDrive)
    assert result.id == "test-drive-1"
    assert result.status == TestDriveStatus.COMPLETED