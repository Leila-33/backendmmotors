from unittest.mock import Mock

import pytest

from modules.auth.application.services.activation_token_validator import (
    ActivationTokenValidator,
)

from modules.auth.domain.exceptions import (
    InvalidActivationToken,
    ActivationTokenExpired,
    ActivationTokenAlreadyUsed,
)


def create_validator():
    repository = Mock()

    validator = ActivationTokenValidator(
        activation_token_repository=repository,
    )

    return validator, repository

def test_get_activation_returns_activation():
    validator, repository = create_validator()

    activation = Mock()

    repository.find_by_token.return_value = activation

    result = validator.get_activation("raw-token")

    assert result is activation

    repository.find_by_token.assert_called_once_with(
        "raw-token"
    )

def test_get_activation_raises_when_token_does_not_exist():
    validator, repository = create_validator()

    repository.find_by_token.return_value = None

    with pytest.raises(InvalidActivationToken):
        validator.get_activation("invalid-token")

    repository.find_by_token.assert_called_once_with(
        "invalid-token"
    )

def test_validate_for_activation_raises_when_token_already_used():
    validator, repository = create_validator()

    activation = Mock()

    activation.is_used.return_value = True

    with pytest.raises(ActivationTokenAlreadyUsed):
        validator.validate_for_activation(activation)

    activation.is_used.assert_called_once()

    activation.is_expired.assert_not_called()

def test_validate_for_activation_raises_when_token_is_expired():
    validator, repository = create_validator()

    activation = Mock()

    activation.is_used.return_value = False
    activation.is_expired.return_value = True

    with pytest.raises(ActivationTokenExpired):
        validator.validate_for_activation(activation)

    activation.is_used.assert_called_once()
    activation.is_expired.assert_called_once()

def test_validate_for_activation_returns_activation_when_valid():
    validator, repository = create_validator()

    activation = Mock()

    activation.is_used.return_value = False
    activation.is_expired.return_value = False

    result = validator.validate_for_activation(activation)

    assert result is activation

    activation.is_used.assert_called_once()
    activation.is_expired.assert_called_once()

def test_validate_for_activation_checks_used_before_expired():
    validator, repository = create_validator()

    activation = Mock()

    activation.is_used.return_value = True
    activation.is_expired.return_value = True

    with pytest.raises(ActivationTokenAlreadyUsed):
        validator.validate_for_activation(activation)

    activation.is_used.assert_called_once()
    activation.is_expired.assert_not_called()