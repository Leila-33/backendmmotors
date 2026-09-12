from unittest.mock import Mock

import pytest

from modules.auth.application.use_cases.admin.create_user import (
    CreateUserUseCase,
)
from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from modules.applications.domain.enums import EventType


def create_user() -> User:
    return User(
        id="user-123",
        first_name="Leila",
        last_name="El",
        email="leila.el@example.com",
        password="hashed-password",
        role=UserRole.CLIENT,
        is_verified=True,
        is_active=True,
        accepted_cgu=True,
        is_deleted=False,
        deleted_at=None,
    )


def create_dto():
    return Mock(
        first_name="Leila",
        last_name="El",
        email="leila.el@example.com",
        password="hashed-password",
        role=UserRole.CLIENT,
    )


def test_create_user_success():
    user_creation_service = Mock()
    event_service = Mock()
    uow = Mock()

    user = create_user()

    user_creation_service.create_user.return_value = user

    dto = create_dto()

    use_case = CreateUserUseCase(
        user_creation_service=user_creation_service,
        event_service=event_service,
        uow=uow,
    )

    result = use_case.execute(
        dto=dto,
        admin_id="admin-123",
    )

    # Résultat
    assert result.id == "user-123"
    assert result.email == "leila.el@example.com"
    assert result.role == UserRole.CLIENT

    # Création de l'utilisateur
    user_creation_service.create_user.assert_called_once_with(
        first_name="Leila",
        last_name="El",
        email="leila.el@example.com",
        password="hashed-password",
        role=UserRole.CLIENT,
    )

    # Event
    event_service.log.assert_called_once()

    event = event_service.log.call_args.kwargs

    assert event["type"] == EventType.USER_CREATED
    assert event["message"] == (
        "Utilisateur créé par un administrateur"
    )
    assert event["user_id"] == "admin-123"

    assert event["event_metadata"] == {
        "email": "leila.el@example.com",
        "role": UserRole.CLIENT.value,
    }

    # Transaction
    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_create_user_rollback_when_creation_fails():
    user_creation_service = Mock()
    event_service = Mock()
    uow = Mock()

    user_creation_service.create_user.side_effect = (
        RuntimeError("Database error")
    )

    dto = create_dto()

    use_case = CreateUserUseCase(
        user_creation_service=user_creation_service,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-123",
        )

    user_creation_service.create_user.assert_called_once()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_create_user_rollback_when_event_logging_fails():
    user_creation_service = Mock()
    event_service = Mock()
    uow = Mock()

    user = create_user()

    user_creation_service.create_user.return_value = user

    event_service.log.side_effect = RuntimeError(
        "Event logging error"
    )

    dto = create_dto()

    use_case = CreateUserUseCase(
        user_creation_service=user_creation_service,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        RuntimeError,
        match="Event logging error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-123",
        )

    user_creation_service.create_user.assert_called_once()

    event_service.log.assert_called_once()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_create_user_rollback_when_commit_fails():
    user_creation_service = Mock()
    event_service = Mock()
    uow = Mock()

    user = create_user()

    user_creation_service.create_user.return_value = user

    uow.commit.side_effect = RuntimeError(
        "Commit error"
    )

    dto = create_dto()

    use_case = CreateUserUseCase(
        user_creation_service=user_creation_service,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(
            dto=dto,
            admin_id="admin-123",
        )

    user_creation_service.create_user.assert_called_once()

    event_service.log.assert_called_once()

    uow.commit.assert_called_once()
    uow.rollback.assert_called_once()