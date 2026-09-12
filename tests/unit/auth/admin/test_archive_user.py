from datetime import timezone
from unittest.mock import Mock

import pytest

from modules.auth.application.use_cases.admin.archive_user import (
    ArchiveUserUseCase,
)
from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import (
    CannotArchiveAdmin,
    UserNotFound,
)
from modules.applications.domain.enums import EventType


def create_user(
    role=UserRole.CLIENT,
) -> User:
    return User(
        id="user-123",
        first_name="Leila",
        last_name="El",
        email="leila.el@example.com",
        password="hashed-password",
        role=role,
        is_verified=True,
        is_active=True,
        accepted_cgu=True,
        is_deleted=False,
        deleted_at=None,
    )


def test_archive_user_success():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user = create_user()

    user_repo.get_by_id.return_value = user

    use_case = ArchiveUserUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    result = use_case.execute(
        user_id="user-123",
        admin_id="admin-123",
    )

    assert result.user_id == "user-123"

    assert user.is_deleted is True
    assert user.is_active is False
    assert user.deleted_at is not None
    assert user.deleted_at.tzinfo == timezone.utc

    user_repo.get_by_id.assert_called_once_with(
        "user-123"
    )

    user_repo.update.assert_called_once_with(
        user
    )

    event_service.log.assert_called_once()

    event = event_service.log.call_args.kwargs

    assert event["type"] == EventType.USER_ARCHIVED
    assert event["message"] == "Utilisateur archivé"
    assert event["user_id"] == "admin-123"

    assert event["event_metadata"]["email"] == (
        "leila.el@example.com"
    )

    assert event["event_metadata"]["role"] == (
        UserRole.CLIENT.value
    )

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_archive_user_not_found():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user_repo.get_by_id.return_value = None

    use_case = ArchiveUserUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(UserNotFound):
        use_case.execute(
            user_id="user-123",
            admin_id="admin-123",
        )

    user_repo.get_by_id.assert_called_once_with(
        "user-123"
    )

    user_repo.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_archive_user_cannot_archive_admin():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    admin = create_user(
        role=UserRole.ADMIN
    )

    user_repo.get_by_id.return_value = admin

    use_case = ArchiveUserUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(CannotArchiveAdmin):
        use_case.execute(
            user_id="user-123",
            admin_id="admin-123",
        )

    user_repo.get_by_id.assert_called_once_with(
        "user-123"
    )

    user_repo.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_archive_user_rollback_when_update_fails():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user = create_user()

    user_repo.get_by_id.return_value = user

    user_repo.update.side_effect = RuntimeError(
        "Database error"
    )

    use_case = ArchiveUserUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(
            user_id="user-123",
            admin_id="admin-123",
        )

    user_repo.get_by_id.assert_called_once_with(
        "user-123"
    )

    user_repo.update.assert_called_once_with(
        user
    )

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_archive_user_rollback_when_event_logging_fails():
    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user = create_user()

    user_repo.get_by_id.return_value = user

    event_service.log.side_effect = RuntimeError(
        "Event logging error"
    )

    use_case = ArchiveUserUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        RuntimeError,
        match="Event logging error",
    ):
        use_case.execute(
            user_id="user-123",
            admin_id="admin-123",
        )

    user_repo.get_by_id.assert_called_once_with(
        "user-123"
    )

    user_repo.update.assert_called_once_with(
        user
    )

    event_service.log.assert_called_once()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()