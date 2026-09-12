from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from modules.auth.application.services.activation_token_service import (
    ActivationTokenService,
)
import hashlib

def create_service():
    repository = Mock()

    service = ActivationTokenService(
        repository=repository,
    )

    return service, repository


def test_create_activation_token_success():
    service, repository = create_service()

    before = datetime.now(timezone.utc)

    with patch(
        "modules.auth.application.services.activation_token_service.secrets.token_urlsafe",
        return_value="raw-token",
    ), patch(
        "modules.auth.application.services.activation_token_service.uuid.uuid4",
        return_value="token-uuid",
    ):

        result = service.create(
            user_id="user-123",
            quote_id="quote-123",
        )

    after = datetime.now(timezone.utc)

    assert result == "raw-token"

    repository.save.assert_called_once()

    model = repository.save.call_args.args[0]

    assert model.id == "token-uuid"
    assert model.user_id == "user-123"
    assert model.quote_id == "quote-123"

    assert model.token_hash == hashlib.sha256(
        b"raw-token"
    ).hexdigest()

    assert (
        before + timedelta(hours=48)
        <= model.expires_at
        <= after + timedelta(hours=48)
    )

def test_create_activation_token_without_quote():
    service, repository = create_service()

    with patch(
        "modules.auth.application.services.activation_token_service.secrets.token_urlsafe",
        return_value="raw-token",
    ):
        result = service.create(
            user_id="user-123",
        )

    assert result == "raw-token"

    repository.save.assert_called_once()

    model = repository.save.call_args.args[0]

    assert model.user_id == "user-123"
    assert model.quote_id is None

def test_create_returns_raw_token_not_hash():
    service, repository = create_service()

    with patch(
        "modules.auth.application.services.activation_token_service.secrets.token_urlsafe",
        return_value="raw-token",
    ):
        result = service.create(
            user_id="user-123",
        )

    model = repository.save.call_args.args[0]

    assert result == "raw-token"
    assert result != model.token_hash

def test_create_saves_activation_token():
    service, repository = create_service()

    with patch(
        "modules.auth.application.services.activation_token_service.secrets.token_urlsafe",
        return_value="raw-token",
    ):
        service.create(
            user_id="user-123",
            quote_id="quote-456",
        )

    repository.save.assert_called_once()

    model = repository.save.call_args.args[0]

    assert model.user_id == "user-123"
    assert model.quote_id == "quote-456"

import pytest


def test_create_propagates_repository_error():
    service, repository = create_service()

    repository.save.side_effect = RuntimeError(
        "Database error"
    )

    with patch(
        "modules.auth.application.services.activation_token_service.secrets.token_urlsafe",
        return_value="raw-token",
    ):
        with pytest.raises(
            RuntimeError,
            match="Database error",
        ):
            service.create(
                user_id="user-123",
            )