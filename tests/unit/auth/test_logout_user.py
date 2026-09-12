from unittest.mock import Mock

import pytest

from modules.auth.application.results.message_result import MessageResult
from modules.auth.application.use_cases.logout_user import LogoutUserUseCase
from modules.auth.domain.exceptions import InvalidRefreshToken


def create_jwt_service():
    jwt_service = Mock()
    jwt_service.decode.return_value = {
        "jti": "refresh-jti",
        "sub": "user-1",
    }
    return jwt_service


def create_use_case():
    refresh_repository = Mock()
    jwt_service = create_jwt_service()
    uow = Mock()

    use_case = LogoutUserUseCase(
        refresh_repository=refresh_repository,
        jwt_service=jwt_service,
        uow=uow,
    )

    return use_case, refresh_repository, jwt_service, uow


def test_logout_user_success():
    use_case, refresh_repository, jwt_service, uow = create_use_case()

    result = use_case.execute("refresh-token")

    assert isinstance(result, MessageResult)
    assert result.message == "Déconnexion réussie"

    jwt_service.decode.assert_called_once_with(
        "refresh-token"
    )

    refresh_repository.revoke_by_jti.assert_called_once_with(
        "refresh-jti"
    )

    uow.commit.assert_called_once_with()
    uow.rollback.assert_not_called()


def test_logout_user_invalid_refresh_token_when_jti_is_missing():
    use_case, refresh_repository, jwt_service, uow = create_use_case()

    jwt_service.decode.return_value = {
        "sub": "user-1",
    }

    with pytest.raises(InvalidRefreshToken):
        use_case.execute("refresh-token")

    jwt_service.decode.assert_called_once_with(
        "refresh-token"
    )

    refresh_repository.revoke_by_jti.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


def test_logout_user_invalid_refresh_token_when_jti_is_empty():
    use_case, refresh_repository, jwt_service, uow = create_use_case()

    jwt_service.decode.return_value = {
        "jti": "",
        "sub": "user-1",
    }

    with pytest.raises(InvalidRefreshToken):
        use_case.execute("refresh-token")

    refresh_repository.revoke_by_jti.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


def test_logout_user_rollback_when_revoke_fails():
    use_case, refresh_repository, jwt_service, uow = create_use_case()

    refresh_repository.revoke_by_jti.side_effect = Exception(
        "Erreur base de données"
    )

    with pytest.raises(Exception, match="Erreur base de données"):
        use_case.execute("refresh-token")

    jwt_service.decode.assert_called_once_with(
        "refresh-token"
    )

    refresh_repository.revoke_by_jti.assert_called_once_with(
        "refresh-jti"
    )

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once_with()


def test_logout_user_rollback_when_commit_fails():
    use_case, refresh_repository, jwt_service, uow = create_use_case()

    uow.commit.side_effect = Exception(
        "Erreur commit"
    )

    with pytest.raises(Exception, match="Erreur commit"):
        use_case.execute("refresh-token")

    refresh_repository.revoke_by_jti.assert_called_once_with(
        "refresh-jti"
    )

    uow.commit.assert_called_once_with()
    uow.rollback.assert_called_once_with()


def test_logout_user_rollback_when_decode_fails():
    use_case, refresh_repository, jwt_service, uow = create_use_case()

    jwt_service.decode.side_effect = Exception(
        "Token illisible"
    )

    with pytest.raises(Exception, match="Token illisible"):
        use_case.execute("refresh-token")

    refresh_repository.revoke_by_jti.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_called_once_with()