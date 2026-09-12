from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.auth.application.results.message_result import (
    MessageResult,
)
from modules.auth.application.use_cases.verify_email import (
    VerifyEmailUseCase,
)
from modules.auth.domain.exceptions import TokenInvalid


def create_jwt_service():
    jwt_service = Mock()

    jwt_service.decode.return_value = {
        "type": "email_verification",
        "sub": "user-1",
    }

    return jwt_service


def create_user(
    user_id="user-1",
    is_verified=False,
):
    user = Mock()

    user.id = user_id
    user.email = "user@example.com"
    user.is_verified = is_verified

    return user


def create_use_case():
    user_repo = Mock()
    jwt_service = create_jwt_service()
    event_service = Mock()
    uow = Mock()

    use_case = VerifyEmailUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        event_service=event_service,
        uow=uow,
    )

    return (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    )


def test_verify_email_success():
    (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    user = create_user()

    user_repo.get_by_id.return_value = user

    result = use_case.execute(
        "verification-token"
    )

    assert isinstance(
        result,
        MessageResult,
    )

    assert result.message == "Email vérifié"

    jwt_service.decode.assert_called_once_with(
        "verification-token"
    )

    user_repo.get_by_id.assert_called_once_with(
        "user-1"
    )

    assert user.is_verified is True

    user_repo.update.assert_called_once_with(
        user
    )

    event_service.log.assert_called_once_with(
        type=EventType.USER_EMAIL_VERIFIED,
        message="Email utilisateur vérifié",
        user_id="user-1",
        event_metadata={
            "action": "email_verified",
        },
    )

    uow.commit.assert_called_once_with()
    uow.rollback.assert_not_called()


def test_verify_email_invalid_token_type():
    (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    jwt_service.decode.return_value = {
        "type": "password_reset",
        "sub": "user-1",
    }

    with pytest.raises(TokenInvalid):
        use_case.execute(
            "verification-token"
        )

    jwt_service.decode.assert_called_once_with(
        "verification-token"
    )

    user_repo.get_by_id.assert_not_called()
    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()

    # TokenInvalid possède son propre except,
    # donc aucun rollback.
    uow.rollback.assert_not_called()


def test_verify_email_invalid_token_when_user_id_is_missing():
    (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    jwt_service.decode.return_value = {
        "type": "email_verification",
    }

    with pytest.raises(TokenInvalid):
        use_case.execute(
            "verification-token"
        )

    jwt_service.decode.assert_called_once_with(
        "verification-token"
    )

    user_repo.get_by_id.assert_not_called()
    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


def test_verify_email_invalid_token_when_user_does_not_exist():
    (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    user_repo.get_by_id.return_value = None

    with pytest.raises(TokenInvalid):
        use_case.execute(
            "verification-token"
        )

    jwt_service.decode.assert_called_once_with(
        "verification-token"
    )

    user_repo.get_by_id.assert_called_once_with(
        "user-1"
    )

    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


def test_verify_email_already_verified():
    (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    user = create_user(
        is_verified=True
    )

    user_repo.get_by_id.return_value = user

    result = use_case.execute(
        "verification-token"
    )

    assert isinstance(
        result,
        MessageResult,
    )

    assert result.message == "Email déjà vérifié"

    jwt_service.decode.assert_called_once_with(
        "verification-token"
    )

    user_repo.get_by_id.assert_called_once_with(
        "user-1"
    )

    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()
    uow.commit.assert_not_called()
    uow.rollback.assert_not_called()


def test_verify_email_rollback_when_update_fails():
    (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    user = create_user()

    user_repo.get_by_id.return_value = user

    user_repo.update.side_effect = Exception(
        "Erreur mise à jour utilisateur"
    )

    with pytest.raises(
        Exception,
        match="Erreur mise à jour utilisateur",
    ):
        use_case.execute(
            "verification-token"
        )

    assert user.is_verified is True

    user_repo.update.assert_called_once_with(
        user
    )

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once_with()


def test_verify_email_rollback_when_event_logging_fails():
    (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    user = create_user()

    user_repo.get_by_id.return_value = user

    event_service.log.side_effect = Exception(
        "Erreur journalisation événement"
    )

    with pytest.raises(
        Exception,
        match="Erreur journalisation événement",
    ):
        use_case.execute(
            "verification-token"
        )

    assert user.is_verified is True

    user_repo.update.assert_called_once_with(
        user
    )

    event_service.log.assert_called_once_with(
        type=EventType.USER_EMAIL_VERIFIED,
        message="Email utilisateur vérifié",
        user_id="user-1",
        event_metadata={
            "action": "email_verified",
        },
    )

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once_with()


def test_verify_email_rollback_when_commit_fails():
    (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    user = create_user()

    user_repo.get_by_id.return_value = user

    uow.commit.side_effect = Exception(
        "Erreur commit"
    )

    with pytest.raises(
        Exception,
        match="Erreur commit",
    ):
        use_case.execute(
            "verification-token"
        )

    assert user.is_verified is True

    user_repo.update.assert_called_once_with(
        user
    )

    event_service.log.assert_called_once_with(
        type=EventType.USER_EMAIL_VERIFIED,
        message="Email utilisateur vérifié",
        user_id="user-1",
        event_metadata={
            "action": "email_verified",
        },
    )

    uow.commit.assert_called_once_with()
    uow.rollback.assert_called_once_with()


def test_verify_email_rollback_when_decode_fails():
    (
        use_case,
        user_repo,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    jwt_service.decode.side_effect = Exception(
        "Token illisible"
    )

    with pytest.raises(
        Exception,
        match="Token illisible",
    ):
        use_case.execute(
            "verification-token"
        )

    jwt_service.decode.assert_called_once_with(
        "verification-token"
    )

    user_repo.get_by_id.assert_not_called()
    user_repo.update.assert_not_called()
    event_service.log.assert_not_called()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once_with()