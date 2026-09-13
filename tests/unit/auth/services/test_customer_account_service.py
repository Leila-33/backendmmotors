import pytest
from unittest.mock import Mock

from modules.auth.application.services.customer_account_service import (
    CustomerAccountService,
)


def create_service():
    user_creation_service = Mock()
    activation_token_service = Mock()
    lead_repository = Mock()

    service = CustomerAccountService(
        user_creation_service=user_creation_service,
        activation_token_service=activation_token_service,
        lead_repository=lead_repository,
    )

    return (
        service,
        user_creation_service,
        activation_token_service,
        lead_repository,
    )


def create_lead():
    lead = Mock()
    lead.id = "lead-123"
    lead.first_name = "leila"
    lead.last_name = "El"
    lead.email = "leila@example.com"

    return lead


def create_user():
    user = Mock()
    user.id = "user-123"
    user.email = "leila@example.com"

    return user

def test_ensure_account_creates_account_and_activation_token():
    (
        service,
        user_creation_service,
        activation_token_service,
        lead_repository,
    ) = create_service()

    lead = create_lead()
    user = create_user()

    user_creation_service.create_client_without_password.return_value = (
        user,
        True,
    )

    activation_token_service.create.return_value = "activation-token"

    result = service.ensure_account(
        lead=lead,
        quote_id="quote-123",
    )

    assert result == {
        "user": user,
        "created": True,
        "token": "activation-token",
    }

    user_creation_service.create_client_without_password.assert_called_once_with(
        first_name="leila",
        last_name="El",
        email="leila@example.com",
    )

    lead_repository.attach_user.assert_called_once_with(
        lead_id="lead-123",
        user_id="user-123",
    )

    activation_token_service.create.assert_called_once_with(
        user_id="user-123",
        quote_id="quote-123",
    )

def test_ensure_account_does_not_create_token_for_existing_account():
    (
        service,
        user_creation_service,
        activation_token_service,
        lead_repository,
    ) = create_service()

    lead = create_lead()
    user = create_user()

    user_creation_service.create_client_without_password.return_value = (
        user,
        False,
    )

    result = service.ensure_account(
        lead=lead,
        quote_id="quote-123",
    )

    assert result == {
        "user": user,
        "created": False,
        "token": None,
    }

    user_creation_service.create_client_without_password.assert_called_once()

    lead_repository.attach_user.assert_called_once_with(
        lead_id="lead-123",
        user_id="user-123",
    )

    activation_token_service.create.assert_not_called()

def test_ensure_account_creates_token_without_quote():
    (
        service,
        user_creation_service,
        activation_token_service,
        lead_repository,
    ) = create_service()

    lead = create_lead()
    user = create_user()

    user_creation_service.create_client_without_password.return_value = (
        user,
        True,
    )

    activation_token_service.create.return_value = "activation-token"

    result = service.ensure_account(lead=lead)

    assert result["created"] is True
    assert result["token"] == "activation-token"

    activation_token_service.create.assert_called_once_with(
        user_id="user-123",
        quote_id=None,
    )

def test_ensure_account_always_attaches_lead_to_user():
    (
        service,
        user_creation_service,
        activation_token_service,
        lead_repository,
    ) = create_service()

    lead = create_lead()
    user = create_user()

    user_creation_service.create_client_without_password.return_value = (
        user,
        False,
    )

    service.ensure_account(lead)

    lead_repository.attach_user.assert_called_once_with(
        lead_id="lead-123",
        user_id="user-123",
    )

def test_ensure_account_propagates_account_creation_error():
    (
        service,
        user_creation_service,
        activation_token_service,
        lead_repository,
    ) = create_service()

    lead = create_lead()

    user_creation_service.create_client_without_password.side_effect = (
        RuntimeError("Database error")
    )

    with pytest.raises(RuntimeError, match="Database error"):
        service.ensure_account(lead)

    lead_repository.attach_user.assert_not_called()
    activation_token_service.create.assert_not_called()

def test_ensure_account_propagates_attach_error():
    (
        service,
        user_creation_service,
        activation_token_service,
        lead_repository,
    ) = create_service()

    lead = create_lead()
    user = create_user()

    user_creation_service.create_client_without_password.return_value = (
        user,
        True,
    )

    lead_repository.attach_user.side_effect = RuntimeError(
        "Attach failed"
    )

    with pytest.raises(RuntimeError, match="Attach failed"):
        service.ensure_account(lead, quote_id="quote-123")

    activation_token_service.create.assert_not_called()

def test_ensure_account_propagates_activation_token_error():
    (
        service,
        user_creation_service,
        activation_token_service,
        lead_repository,
    ) = create_service()

    lead = create_lead()
    user = create_user()

    user_creation_service.create_client_without_password.return_value = (
        user,
        True,
    )

    activation_token_service.create.side_effect = RuntimeError(
        "Token creation failed"
    )

    with pytest.raises(
        RuntimeError,
        match="Token creation failed",
    ):
        service.ensure_account(
            lead=lead,
            quote_id="quote-123",
        )