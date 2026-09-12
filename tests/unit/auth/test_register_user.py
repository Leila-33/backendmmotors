from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.auth.application.results.message_result import (
    MessageResult,
)
from modules.auth.application.use_cases.register_user import (
    RegisterUserUseCase,
)


def create_dto(
    first_name="Leila",
    last_name="El",
    email="Leila@example.com",
    password="Password123!",
    accepted_cgu=True,
):
    dto = Mock()

    dto.first_name = first_name
    dto.last_name = last_name
    dto.email = email
    dto.password = password
    dto.accepted_cgu = accepted_cgu

    return dto


def create_user(
    user_id="user-1",
    email="Leila@example.com",
):
    user = Mock()

    user.id = user_id
    user.email = email

    return user


def create_use_case():
    user_creation_service = Mock()
    jwt_service = Mock()
    email_service = Mock()
    event_service = Mock()
    uow = Mock()

    use_case = RegisterUserUseCase(
        user_creation_service=user_creation_service,
        jwt_service=jwt_service,
        email_service=email_service,
        event_service=event_service,
        uow=uow,
    )

    return (
        use_case,
        user_creation_service,
        jwt_service,
        email_service,
        event_service,
        uow,
    )


def test_register_user_success():
    (
        use_case,
        user_creation_service,
        jwt_service,
        email_service,
        event_service,
        uow,
    ) = create_use_case()

    dto = create_dto()

    user = create_user()

    user_creation_service.create_client.return_value = user

    jwt_service.create_email_token.return_value = (
        "verification-token"
    )

    result = use_case.execute(dto)

    assert isinstance(
        result,
        MessageResult,
    )

    assert result.message == (
        "Utilisateur créé avec succès."
    )

    user_creation_service.create_client.assert_called_once_with(
        first_name="Leila",
        last_name="El",
        email="Leila@example.com",
        password="Password123!",
        accepted_cgu=True,
    )

    event_service.log.assert_called_once_with(
        type=EventType.USER_REGISTERED,
        message="Nouvel utilisateur inscrit",
        user_id="user-1",
        event_metadata={
            "email": "Leila@example.com",
        },
    )

    jwt_service.create_email_token.assert_called_once_with(
        "user-1"
    )

    uow.commit.assert_called_once_with()

    email_service.send_verification_email.assert_called_once_with(
        email="Leila@example.com",
        token="verification-token",
    )

    uow.rollback.assert_not_called()


def test_register_user_rollback_when_user_creation_fails():
    (
        use_case,
        user_creation_service,
        jwt_service,
        email_service,
        event_service,
        uow,
    ) = create_use_case()

    dto = create_dto()

    user_creation_service.create_client.side_effect = Exception(
        "Erreur création utilisateur"
    )

    with pytest.raises(
        Exception,
        match="Erreur création utilisateur",
    ):
        use_case.execute(dto)

    user_creation_service.create_client.assert_called_once()

    event_service.log.assert_not_called()
    jwt_service.create_email_token.assert_not_called()
    uow.commit.assert_not_called()
    email_service.send_verification_email.assert_not_called()

    uow.rollback.assert_called_once_with()


def test_register_user_rollback_when_event_logging_fails():
    (
        use_case,
        user_creation_service,
        jwt_service,
        email_service,
        event_service,
        uow,
    ) = create_use_case()

    dto = create_dto()

    user = create_user()

    user_creation_service.create_client.return_value = user

    event_service.log.side_effect = Exception(
        "Erreur journalisation événement"
    )

    with pytest.raises(
        Exception,
        match="Erreur journalisation événement",
    ):
        use_case.execute(dto)

    user_creation_service.create_client.assert_called_once()

    event_service.log.assert_called_once_with(
        type=EventType.USER_REGISTERED,
        message="Nouvel utilisateur inscrit",
        user_id="user-1",
        event_metadata={
            "email": "Leila@example.com",
        },
    )

    jwt_service.create_email_token.assert_not_called()
    uow.commit.assert_not_called()
    email_service.send_verification_email.assert_not_called()

    uow.rollback.assert_called_once_with()


def test_register_user_rollback_when_email_token_creation_fails():
    (
        use_case,
        user_creation_service,
        jwt_service,
        email_service,
        event_service,
        uow,
    ) = create_use_case()

    dto = create_dto()

    user = create_user()

    user_creation_service.create_client.return_value = user

    jwt_service.create_email_token.side_effect = Exception(
        "Erreur création token"
    )

    with pytest.raises(
        Exception,
        match="Erreur création token",
    ):
        use_case.execute(dto)

    user_creation_service.create_client.assert_called_once()

    event_service.log.assert_called_once()

    jwt_service.create_email_token.assert_called_once_with(
        "user-1"
    )

    uow.commit.assert_not_called()
    email_service.send_verification_email.assert_not_called()

    uow.rollback.assert_called_once_with()


def test_register_user_rollback_when_commit_fails():
    (
        use_case,
        user_creation_service,
        jwt_service,
        email_service,
        event_service,
        uow,
    ) = create_use_case()

    dto = create_dto()

    user = create_user()

    user_creation_service.create_client.return_value = user

    jwt_service.create_email_token.return_value = (
        "verification-token"
    )

    uow.commit.side_effect = Exception(
        "Erreur commit"
    )

    with pytest.raises(
        Exception,
        match="Erreur commit",
    ):
        use_case.execute(dto)

    user_creation_service.create_client.assert_called_once()

    event_service.log.assert_called_once()

    jwt_service.create_email_token.assert_called_once_with(
        "user-1"
    )

    uow.commit.assert_called_once_with()

    email_service.send_verification_email.assert_not_called()

    uow.rollback.assert_called_once_with()


def test_register_user_raises_when_email_sending_fails():
    (
        use_case,
        user_creation_service,
        jwt_service,
        email_service,
        event_service,
        uow,
    ) = create_use_case()

    dto = create_dto()
    user = create_user()

    user_creation_service.create_client.return_value = user
    jwt_service.create_email_token.return_value = "verification-token"

    email_service.send_verification_email.side_effect = Exception(
        "Email sending failed"
    )

    with pytest.raises(Exception, match="Email sending failed"):
        use_case.execute(dto)

    user_creation_service.create_client.assert_called_once()
    event_service.log.assert_called_once()
    jwt_service.create_email_token.assert_called_once_with(user.id)

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()