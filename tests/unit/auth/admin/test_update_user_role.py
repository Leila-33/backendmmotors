from unittest.mock import Mock

import pytest

from modules.auth.application.use_cases.admin.update_user_role import (
    UpdateUserRoleUseCase,
)
from modules.auth.application.dtos.admin.update_user_role_dto import (
    UpdateUserRoleDTO,
)
from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Forbidden, UserNotFound


def create_user(
    user_id: str = "user-1",
    email: str = "user@example.com",
    role: UserRole = UserRole.CLIENT,
    is_active: bool = True,
) -> User:
    return User(
        id=user_id,
        first_name="Leila",
        last_name="El",
        email=email,
        password="hashed-password",
        role=role,
        is_verified=True,
        is_active=is_active,
        accepted_cgu=True,
        is_deleted=False,
    )


def create_dto(
    role: UserRole,
) -> UpdateUserRoleDTO:
    return UpdateUserRoleDTO(
        role=role,
    )


def test_update_user_role_success():

    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user = create_user(
        role=UserRole.CLIENT,
    )

    user_repo.get_by_id.return_value = user

    dto = create_dto(
        role=UserRole.SALES_AGENT,
    )

    use_case = UpdateUserRoleUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    result = use_case.execute(
        user_id="user-1",
        dto=dto,
        admin_id="admin-1",
    )

    assert user.role == UserRole.SALES_AGENT

    assert result.id == "user-1"
    assert result.role == UserRole.SALES_AGENT

    user_repo.get_by_id.assert_called_once_with("user-1")
    user_repo.update.assert_called_once_with(user)

    event_service.log.assert_called_once()

    event_kwargs = event_service.log.call_args.kwargs

    assert event_kwargs["message"] == "Rôle utilisateur modifié"
    assert event_kwargs["user_id"] == "admin-1"
    assert event_kwargs["event_metadata"] == {
        "email": "user@example.com",
        "old_role": UserRole.CLIENT.value,
        "dto.role": UserRole.SALES_AGENT.value,
    }

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_update_user_role_user_not_found():

    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user_repo.get_by_id.return_value = None

    dto = create_dto(
        role=UserRole.SALES_AGENT,
    )

    use_case = UpdateUserRoleUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(UserNotFound):
        use_case.execute(
            user_id="unknown-user",
            dto=dto,
            admin_id="admin-1",
        )

    user_repo.get_by_id.assert_called_once_with(
        "unknown-user"
    )

    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_update_user_role_cannot_modify_admin():

    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    admin = create_user(
        user_id="admin-2",
        email="admin@example.com",
        role=UserRole.ADMIN,
    )

    user_repo.get_by_id.return_value = admin

    dto = create_dto(
        role=UserRole.SALES_AGENT,
    )

    use_case = UpdateUserRoleUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(Forbidden):
        use_case.execute(
            user_id="admin-2",
            dto=dto,
            admin_id="admin-1",
        )

    assert admin.role == UserRole.ADMIN

    user_repo.get_by_id.assert_called_once_with(
        "admin-2"
    )

    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_update_user_role_rollback_when_update_fails():

    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user = create_user(
        role=UserRole.CLIENT,
    )

    user_repo.get_by_id.return_value = user

    user_repo.update.side_effect = RuntimeError(
        "Database error"
    )

    dto = create_dto(
        role=UserRole.SALES_AGENT,
    )

    use_case = UpdateUserRoleUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(
            user_id="user-1",
            dto=dto,
            admin_id="admin-1",
        )

    user_repo.get_by_id.assert_called_once_with(
        "user-1"
    )

    user_repo.update.assert_called_once_with(user)

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_update_user_role_rollback_when_event_logging_fails():

    user_repo = Mock()
    event_service = Mock()
    uow = Mock()

    user = create_user(
        role=UserRole.CLIENT,
    )

    user_repo.get_by_id.return_value = user

    event_service.log.side_effect = RuntimeError(
        "Event logging error"
    )

    dto = create_dto(
        role=UserRole.SALES_AGENT,
    )

    use_case = UpdateUserRoleUseCase(
        user_repo=user_repo,
        event_service=event_service,
        uow=uow,
    )

    with pytest.raises(
        RuntimeError,
        match="Event logging error",
    ):
        use_case.execute(
            user_id="user-1",
            dto=dto,
            admin_id="admin-1",
        )

    assert user.role == UserRole.SALES_AGENT

    user_repo.get_by_id.assert_called_once_with(
        "user-1"
    )

    user_repo.update.assert_called_once_with(user)

    event_service.log.assert_called_once()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()