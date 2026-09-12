from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import pytest

from modules.applications.domain.enums import EventType
from modules.auth.application.dtos.activate_account_dto import (
    ActivateAccountDTO,
)
from modules.auth.application.results.activate_account_result import (
    ActivateAccountResult,
)
from modules.auth.application.use_cases.activate_account import (
    ActivateAccountUseCase,
)
from modules.auth.domain.entities.refresh_token import RefreshToken
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import (
    CguNotAccepted,
    InvalidActivationToken,
)


def create_dto(
    token="activation-token",
    password="Password123!",
    accepted_cgu=True,
):
    return ActivateAccountDTO(
        token=token,
        password=password,
        accepted_cgu=accepted_cgu,
    )


def create_user():
    user = Mock()
    user.id = "user-1"
    user.email = "user@example.com"
    user.role = UserRole.CLIENT
    return user


def create_activation(
    user_id="user-1",
    quote_id="quote-1",
):
    activation = Mock()
    activation.user_id = user_id
    activation.quote_id = quote_id
    return activation


def create_use_case():
    validator = Mock()
    activation_token_repository = Mock()
    user_repository = Mock()
    refresh_repository = Mock()
    jwt_service = Mock()
    event_service = Mock()
    uow = Mock()

    use_case = ActivateAccountUseCase(
        validator=validator,
        activation_token_repository=activation_token_repository,
        user_repository=user_repository,
        refresh_repository=refresh_repository,
        jwt_service=jwt_service,
        event_service=event_service,
        uow=uow,
    )

    return (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    )


def configure_success(
    validator,
    user_repository,
    jwt_service,
):
    activation = create_activation()
    user = create_user()

    validator.get_activation.return_value = activation
    user_repository.get_by_id.return_value = user

    jwt_service.create_access_token.return_value = "access-token"
    jwt_service.create_refresh_token.return_value = "refresh-token"
    jwt_service.decode.return_value = {
        "jti": "refresh-jti",
    }

    return activation, user


def test_activate_account_success():
    (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    activation, user = configure_success(
        validator,
        user_repository,
        jwt_service,
    )

    dto = create_dto()

    fixed_now = datetime(
        2026,
        1,
        1,
        12,
        0,
        tzinfo=timezone.utc,
    )

    with patch(
        "modules.auth.application.use_cases.activate_account.hash_password",
        return_value="hashed-password",
    ), patch(
        "modules.auth.application.use_cases.activate_account.datetime"
    ) as mock_datetime:

        mock_datetime.now.return_value = fixed_now

        result = use_case.execute(dto)

    assert isinstance(result, ActivateAccountResult)

    assert result.message == "Compte activé avec succès"
    assert result.access_token == "access-token"
    assert result.refresh_token == "refresh-token"
    assert result.redirect == "/quotes/quote-1"

    validator.get_activation.assert_called_once_with(
        "activation-token"
    )

    validator.validate_for_activation.assert_called_once_with(
        activation
    )

    user_repository.get_by_id.assert_called_once_with(
        "user-1"
    )

    user.activate.assert_called_once_with(
        hashed_password="hashed-password"
    )

    activation.consume.assert_called_once_with(
        fixed_now
    )

    user_repository.update.assert_called_once_with(
        user
    )

    activation_token_repository.update.assert_called_once_with(
        activation
    )

    event_service.log.assert_called_once_with(
        type=EventType.USER_ACCOUNT_ACTIVATED,
        message="Compte utilisateur activé",
        user_id="user-1",
        event_metadata={
            "email": "user@example.com",
        },
    )

    jwt_service.create_access_token.assert_called_once_with(
        user_id="user-1",
        role=UserRole.CLIENT,
    )

    jwt_service.create_refresh_token.assert_called_once_with(
        user_id="user-1",
        role=UserRole.CLIENT,
    )

    jwt_service.decode.assert_called_once_with(
        "refresh-token"
    )

    refresh_repository.save.assert_called_once()

    refresh_entity = (
        refresh_repository.save.call_args.args[0]
    )

    assert isinstance(
        refresh_entity,
        RefreshToken,
    )

    assert refresh_entity.id == "refresh-jti"
    assert refresh_entity.user_id == "user-1"
    assert refresh_entity.role == UserRole.CLIENT
    assert refresh_entity.jti == "refresh-jti"
    assert refresh_entity.expires_at == (
        fixed_now + timedelta(days=7)
    )
    assert refresh_entity.created_at == fixed_now
    assert refresh_entity.revoked is False

    uow.commit.assert_called_once_with()
    uow.rollback.assert_not_called()


def test_activate_account_redirects_to_home_when_no_quote():
    (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    activation, user = configure_success(
        validator,
        user_repository,
        jwt_service,
    )

    activation.quote_id = None

    dto = create_dto()

    with patch(
        "modules.auth.application.use_cases.activate_account.hash_password",
        return_value="hashed-password",
    ):
        result = use_case.execute(dto)

    assert result.redirect == "/"


def test_activate_account_cgu_not_accepted():
    (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    dto = create_dto(
        accepted_cgu=False
    )

    with pytest.raises(CguNotAccepted):
        use_case.execute(dto)

    validator.get_activation.assert_called_once_with(
        "activation-token"
    )

    validator.validate_for_activation.assert_called_once()

    user_repository.get_by_id.assert_not_called()
    activation_token_repository.update.assert_not_called()
    refresh_repository.save.assert_not_called()
    jwt_service.create_access_token.assert_not_called()
    jwt_service.create_refresh_token.assert_not_called()
    uow.commit.assert_not_called()

    uow.rollback.assert_called_once_with()


def test_activate_account_invalid_token_during_validation():
    (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    validator.get_activation.side_effect = (
        InvalidActivationToken()
    )

    dto = create_dto()

    with pytest.raises(InvalidActivationToken):
        use_case.execute(dto)

    validator.get_activation.assert_called_once_with(
        "activation-token"
    )

    validator.validate_for_activation.assert_not_called()
    user_repository.get_by_id.assert_not_called()
    refresh_repository.save.assert_not_called()
    uow.commit.assert_not_called()

    uow.rollback.assert_called_once_with()


def test_activate_account_invalid_token_when_user_not_found():
    (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    activation = create_activation()

    validator.get_activation.return_value = activation
    user_repository.get_by_id.return_value = None

    dto = create_dto()

    with pytest.raises(InvalidActivationToken):
        use_case.execute(dto)

    validator.validate_for_activation.assert_called_once_with(
        activation
    )

    user_repository.get_by_id.assert_called_once_with(
        "user-1"
    )

    refresh_repository.save.assert_not_called()
    uow.commit.assert_not_called()

    uow.rollback.assert_called_once_with()


def test_activate_account_rollback_when_user_update_fails():
    (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    activation, user = configure_success(
        validator,
        user_repository,
        jwt_service,
    )

    user_repository.update.side_effect = Exception(
        "Erreur mise à jour utilisateur"
    )

    dto = create_dto()

    with patch(
        "modules.auth.application.use_cases.activate_account.hash_password",
        return_value="hashed-password",
    ):
        with pytest.raises(
            Exception,
            match="Erreur mise à jour utilisateur",
        ):
            use_case.execute(dto)

    user.activate.assert_called_once()
    activation.consume.assert_called_once()

    user_repository.update.assert_called_once_with(
        user
    )

    activation_token_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    refresh_repository.save.assert_not_called()
    uow.commit.assert_not_called()

    uow.rollback.assert_called_once_with()


def test_activate_account_rollback_when_event_logging_fails():
    (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    activation, user = configure_success(
        validator,
        user_repository,
        jwt_service,
    )

    event_service.log.side_effect = Exception(
        "Erreur journalisation événement"
    )

    dto = create_dto()

    with patch(
        "modules.auth.application.use_cases.activate_account.hash_password",
        return_value="hashed-password",
    ):
        with pytest.raises(
            Exception,
            match="Erreur journalisation événement",
        ):
            use_case.execute(dto)

    user_repository.update.assert_called_once_with(
        user
    )

    activation_token_repository.update.assert_called_once_with(
        activation
    )

    event_service.log.assert_called_once()

    jwt_service.create_access_token.assert_not_called()
    refresh_repository.save.assert_not_called()
    uow.commit.assert_not_called()

    uow.rollback.assert_called_once_with()


def test_activate_account_rollback_when_refresh_token_save_fails():
    (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    activation, user = configure_success(
        validator,
        user_repository,
        jwt_service,
    )

    refresh_repository.save.side_effect = Exception(
        "Erreur sauvegarde refresh token"
    )

    dto = create_dto()

    with patch(
        "modules.auth.application.use_cases.activate_account.hash_password",
        return_value="hashed-password",
    ):
        with pytest.raises(
            Exception,
            match="Erreur sauvegarde refresh token",
        ):
            use_case.execute(dto)

    refresh_repository.save.assert_called_once()

    uow.commit.assert_not_called()
    uow.rollback.assert_called_once_with()


def test_activate_account_rollback_when_commit_fails():
    (
        use_case,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ) = create_use_case()

    activation, user = configure_success(
        validator,
        user_repository,
        jwt_service,
    )

    uow.commit.side_effect = Exception(
        "Erreur commit"
    )

    dto = create_dto()

    with patch(
        "modules.auth.application.use_cases.activate_account.hash_password",
        return_value="hashed-password",
    ):
        with pytest.raises(
            Exception,
            match="Erreur commit",
        ):
            use_case.execute(dto)

    uow.commit.assert_called_once_with()
    uow.rollback.assert_called_once_with()