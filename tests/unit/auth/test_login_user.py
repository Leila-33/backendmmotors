from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from modules.auth.application.dtos.login_user_dto import LoginUserDTO
from modules.auth.application.results.login_user_result import (
    LoginUserResult,
)
from modules.auth.application.use_cases.login_user import (
    LoginUserUseCase,
)
from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import (
    AccountDeleted,
    AccountDisabled,
    EmailNotVerified,
    InvalidCredentials,
)


def create_user(
    user_id: str = "user-1",
    email: str = "user@example.com",
    password: str = "hashed-password",
    role: UserRole = UserRole.CLIENT,
    is_active: bool = True,
    is_verified: bool = True,
    is_deleted: bool = False,
) -> User:
    return User(
        id=user_id,
        first_name="Leila",
        last_name="El",
        email=email,
        password=password,
        role=role,
        is_verified=is_verified,
        is_active=is_active,
        accepted_cgu=True,
        is_deleted=is_deleted,
    )


def create_dto(
    email: str = "user@example.com",
    password: str = "password123",
) -> LoginUserDTO:
    return LoginUserDTO(
        email=email,
        password=password,
    )


def create_jwt_service():
    jwt_service = Mock()

    jwt_service.create_access_token.return_value = "access-token"
    jwt_service.create_refresh_token.return_value = "refresh-token"

    jwt_service.decode.return_value = {
        "jti": "refresh-jti",
        "exp": 1_900_000_000,
    }

    return jwt_service


def test_login_user_success():

    user_repo = Mock()
    jwt_service = create_jwt_service()
    refresh_repo = Mock()
    uow = Mock()

    user = create_user()

    user_repo.get_by_email.return_value = user

    dto = create_dto()

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow,
    )

    with patch(
        "modules.auth.application.use_cases.login_user.verify_password",
        return_value=True,
    ):

        result = use_case.execute(dto)

    assert isinstance(result, LoginUserResult)

    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"

    user_repo.get_by_email.assert_called_once_with(
        "user@example.com"
    )

    jwt_service.create_access_token.assert_called_once_with(
        "user-1",
        UserRole.CLIENT,
    )

    jwt_service.create_refresh_token.assert_called_once_with(
        "user-1",
        UserRole.CLIENT,
    )

    jwt_service.decode.assert_called_once_with(
        "refresh-token"
    )

    refresh_repo.save.assert_called_once()

    saved_refresh_token = (
        refresh_repo.save.call_args.args[0]
    )

    assert saved_refresh_token.id == "refresh-jti"
    assert saved_refresh_token.user_id == "user-1"
    assert saved_refresh_token.role == UserRole.CLIENT
    assert saved_refresh_token.jti == "refresh-jti"
    assert saved_refresh_token.revoked is False
    assert saved_refresh_token.expires_at == datetime.fromtimestamp(
        1_900_000_000,
        tz=timezone.utc,
    )

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_login_user_invalid_credentials_when_user_not_found():

    user_repo = Mock()
    jwt_service = create_jwt_service()
    refresh_repo = Mock()
    uow = Mock()

    user_repo.get_by_email.return_value = None

    dto = create_dto()

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow,
    )

    with pytest.raises(InvalidCredentials):

        use_case.execute(dto)

    user_repo.get_by_email.assert_called_once_with(
        "user@example.com"
    )

    jwt_service.create_access_token.assert_not_called()
    jwt_service.create_refresh_token.assert_not_called()
    refresh_repo.save.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_login_user_invalid_credentials_when_password_is_wrong():

    user_repo = Mock()
    jwt_service = create_jwt_service()
    refresh_repo = Mock()
    uow = Mock()

    user = create_user()

    user_repo.get_by_email.return_value = user

    dto = create_dto(
        password="wrong-password",
    )

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow,
    )

    with patch(
        "modules.auth.application.use_cases.login_user.verify_password",
        return_value=False,
    ):

        with pytest.raises(InvalidCredentials):

            use_case.execute(dto)

    user_repo.get_by_email.assert_called_once_with(
        "user@example.com"
    )

    jwt_service.create_access_token.assert_not_called()
    jwt_service.create_refresh_token.assert_not_called()
    refresh_repo.save.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_login_user_account_deleted():

    user_repo = Mock()
    jwt_service = create_jwt_service()
    refresh_repo = Mock()
    uow = Mock()

    user = create_user(
        is_deleted=True,
    )

    user_repo.get_by_email.return_value = user

    dto = create_dto()

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow,
    )

    with patch(
        "modules.auth.application.use_cases.login_user.verify_password",
        return_value=True,
    ):

        with pytest.raises(AccountDeleted):

            use_case.execute(dto)

    jwt_service.create_access_token.assert_not_called()
    jwt_service.create_refresh_token.assert_not_called()
    refresh_repo.save.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_login_user_account_disabled():

    user_repo = Mock()
    jwt_service = create_jwt_service()
    refresh_repo = Mock()
    uow = Mock()

    user = create_user(
        is_active=False,
    )

    user_repo.get_by_email.return_value = user

    dto = create_dto()

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow,
    )

    with patch(
        "modules.auth.application.use_cases.login_user.verify_password",
        return_value=True,
    ):

        with pytest.raises(AccountDisabled):

            use_case.execute(dto)

    jwt_service.create_access_token.assert_not_called()
    jwt_service.create_refresh_token.assert_not_called()
    refresh_repo.save.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_login_user_email_not_verified():

    user_repo = Mock()
    jwt_service = create_jwt_service()
    refresh_repo = Mock()
    uow = Mock()

    user = create_user(
        is_verified=False,
    )

    user_repo.get_by_email.return_value = user

    dto = create_dto()

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow,
    )

    with patch(
        "modules.auth.application.use_cases.login_user.verify_password",
        return_value=True,
    ):

        with pytest.raises(EmailNotVerified):

            use_case.execute(dto)

    jwt_service.create_access_token.assert_not_called()
    jwt_service.create_refresh_token.assert_not_called()
    refresh_repo.save.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_login_user_rollback_when_refresh_token_save_fails():

    user_repo = Mock()
    jwt_service = create_jwt_service()
    refresh_repo = Mock()
    uow = Mock()

    user = create_user()

    user_repo.get_by_email.return_value = user

    refresh_repo.save.side_effect = RuntimeError(
        "Database error"
    )

    dto = create_dto()

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow,
    )

    with patch(
        "modules.auth.application.use_cases.login_user.verify_password",
        return_value=True,
    ):

        with pytest.raises(
            RuntimeError,
            match="Database error",
        ):

            use_case.execute(dto)

    refresh_repo.save.assert_called_once()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once()


def test_login_user_rollback_when_commit_fails():

    user_repo = Mock()
    jwt_service = create_jwt_service()
    refresh_repo = Mock()
    uow = Mock()

    user = create_user()

    user_repo.get_by_email.return_value = user

    uow.commit.side_effect = RuntimeError(
        "Commit error"
    )

    dto = create_dto()

    use_case = LoginUserUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow,
    )

    with patch(
        "modules.auth.application.use_cases.login_user.verify_password",
        return_value=True,
    ):

        with pytest.raises(
            RuntimeError,
            match="Commit error",
        ):

            use_case.execute(dto)

    refresh_repo.save.assert_called_once()

    uow.commit.assert_called_once()
    uow.rollback.assert_called_once()