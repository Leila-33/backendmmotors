from unittest.mock import Mock, patch

import pytest

from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import EmailAlreadyExists
from modules.auth.application.services.user_creation_service import (
    UserCreationService,
)


# ============================================================
# HELPERS
# ============================================================

def create_service():
    user_repository = Mock()

    service = UserCreationService(
        user_repository=user_repository,
    )

    return service, user_repository


def create_existing_user():
    user = Mock()

    user.id = "existing-user"
    user.first_name = "Leila"
    user.last_name = "El"
    user.email = "Leila@example.com"

    return user


# ============================================================
# CREATE CLIENT
# ============================================================

def test_create_client_success():
    service, user_repository = create_service()
    user_repository.get_by_email.return_value = None
    user = User(
        id="user-1",
        first_name="Leila",
        last_name="El",
        email="Leila@example.com",
        password="hashed-password",
        role=UserRole.CLIENT,
        is_verified=False,
        is_active=True,
        accepted_cgu=True,
    )

    user_repository.save.return_value = user

    with patch(
        "modules.auth.application.services.user_creation_service.hash_password",
        return_value="hashed-password",
    ), patch(
        "modules.auth.application.services.user_creation_service.uuid.uuid4",
        return_value="generated-uuid",
    ):

        result = service.create_client(
            first_name="Leila",
            last_name="El",
            email="Leila@example.com",
            password="Password123!",
            accepted_cgu=True,
        )

    assert result == user

    user_repository.get_by_email.assert_called_once_with(
        "Leila@example.com"
    )

    user_repository.save.assert_called_once()

    saved_user = user_repository.save.call_args.args[0]

    assert isinstance(saved_user, User)

    assert saved_user.id == "generated-uuid"
    assert saved_user.first_name == "Leila"
    assert saved_user.last_name == "El"
    assert saved_user.email == "Leila@example.com"
    assert saved_user.password == "hashed-password"
    assert saved_user.role == UserRole.CLIENT
    assert saved_user.is_verified is False
    assert saved_user.is_active is True
    assert saved_user.accepted_cgu is True


def test_create_client_raises_when_email_already_exists():
    service, user_repository = create_service()

    existing_user = create_existing_user()

    user_repository.get_by_email.return_value = existing_user

    with pytest.raises(EmailAlreadyExists):
        service.create_client(
            first_name="Leila",
            last_name="El",
            email="Leila@example.com",
            password="Password123!",
            accepted_cgu=True,
        )

    user_repository.get_by_email.assert_called_once_with(
        "Leila@example.com"
    )

    user_repository.save.assert_not_called()


def test_create_client_hashes_password():
    service, user_repository = create_service()
    user_repository.get_by_email.return_value = None
    user_repository.save.side_effect = lambda user: user

    with patch(
        "modules.auth.application.services.user_creation_service.hash_password",
        return_value="hashed-password",
    ) as mock_hash_password, patch(
        "modules.auth.application.services.user_creation_service.uuid.uuid4",
        return_value="user-id",
    ):

        result = service.create_client(
            first_name="Leila",
            last_name="El",
            email="Leila@example.com",
            password="PlainPassword123!",
            accepted_cgu=True,
        )

    mock_hash_password.assert_called_once_with(
        "PlainPassword123!"
    )

    assert result.password == "hashed-password"


def test_create_client_accepts_cgu_false_by_default():
    service, user_repository = create_service()

    user_repository.save.side_effect = lambda user: user
    user_repository.get_by_email.return_value = None
    with patch(
        "modules.auth.application.services.user_creation_service.hash_password",
        return_value="hashed-password",
    ), patch(
        "modules.auth.application.services.user_creation_service.uuid.uuid4",
        return_value="user-id",
    ):

        result = service.create_client(
            first_name="Leila",
            last_name="El",
            email="Leila@example.com",
            password="Password123!",
        )

    assert result.accepted_cgu is False


# ============================================================
# CREATE CLIENT WITHOUT PASSWORD
# ============================================================

def test_create_client_without_password_returns_existing_user():
    service, user_repository = create_service()

    existing_user = create_existing_user()

    user_repository.get_by_email.return_value = existing_user

    result, created = (
        service.create_client_without_password(
            first_name="Leila",
            last_name="El",
            email="Leila@example.com",
        )
    )

    assert result == existing_user
    assert created is False

    user_repository.get_by_email.assert_called_once_with(
        "Leila@example.com"
    )

    user_repository.save.assert_not_called()


def test_create_client_without_password_creates_new_user():
    service, user_repository = create_service()

    user_repository.get_by_email.return_value = None

    user_repository.save.side_effect = (
        lambda user: user
    )

    with patch(
        "modules.auth.application.services.user_creation_service.secrets.token_urlsafe",
        return_value="temporary-password",
    ) as mock_token, patch(
        "modules.auth.application.services.user_creation_service.hash_password",
        return_value="hashed-temporary-password",
    ) as mock_hash_password, patch(
        "modules.auth.application.services.user_creation_service.uuid.uuid4",
        return_value="generated-uuid",
    ):

        result, created = (
            service.create_client_without_password(
                first_name="Jane",
                last_name="El",
                email="jane@example.com",
            )
        )

    assert created is True

    assert isinstance(result, User)

    assert result.id == "generated-uuid"
    assert result.first_name == "Jane"
    assert result.last_name == "El"
    assert result.email == "jane@example.com"
    assert result.password == "hashed-temporary-password"
    assert result.role == UserRole.CLIENT
    assert result.is_verified is False
    assert result.is_active is False
    assert result.accepted_cgu is False

    mock_token.assert_called_once_with(12)

    mock_hash_password.assert_called_once_with(
        "temporary-password"
    )

    user_repository.save.assert_called_once_with(
        result
    )


def test_create_client_without_password_does_not_generate_password_for_existing_user():
    service, user_repository = create_service()

    existing_user = create_existing_user()

    user_repository.get_by_email.return_value = existing_user

    with patch(
        "modules.auth.application.services.user_creation_service.secrets.token_urlsafe"
    ) as mock_token, patch(
        "modules.auth.application.services.user_creation_service.hash_password"
    ) as mock_hash_password:

        result, created = (
            service.create_client_without_password(
                first_name="Leila",
                last_name="El",
                email="Leila@example.com",
            )
        )

    assert result == existing_user
    assert created is False

    mock_token.assert_not_called()
    mock_hash_password.assert_not_called()

    user_repository.save.assert_not_called()


# ============================================================
# CREATE USER - ADMIN
# ============================================================

def test_create_user_success():
    service, user_repository = create_service()

    user_repository.save.side_effect = (
        lambda user: user
    )
    user_repository.get_by_email.return_value = None
    with patch(
        "modules.auth.application.services.user_creation_service.hash_password",
        return_value="hashed-password",
    ), patch(
        "modules.auth.application.services.user_creation_service.uuid.uuid4",
        return_value="generated-uuid",
    ):

        result = service.create_user(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="AdminPassword123!",
            role=UserRole.ADMIN,
        )

    assert isinstance(result, User)

    assert result.id == "generated-uuid"
    assert result.first_name == "Admin"
    assert result.last_name == "User"
    assert result.email == "admin@example.com"
    assert result.password == "hashed-password"
    assert result.role == UserRole.ADMIN
    assert result.is_verified is True
    assert result.is_active is True
    assert result.accepted_cgu is True

    user_repository.get_by_email.assert_called_once_with(
        "admin@example.com"
    )

    user_repository.save.assert_called_once_with(
        result
    )


def test_create_user_raises_when_email_already_exists():
    service, user_repository = create_service()

    existing_user = create_existing_user()

    user_repository.get_by_email.return_value = existing_user

    with pytest.raises(EmailAlreadyExists):
        service.create_user(
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
            password="AdminPassword123!",
            role=UserRole.ADMIN,
        )

    user_repository.get_by_email.assert_called_once_with(
        "admin@example.com"
    )

    user_repository.save.assert_not_called()


def test_create_user_can_override_verification_and_active_status():
    service, user_repository = create_service()

    user_repository.save.side_effect = (
        lambda user: user
    )
    user_repository.get_by_email.return_value = None
    with patch(
        "modules.auth.application.services.user_creation_service.hash_password",
        return_value="hashed-password",
    ), patch(
        "modules.auth.application.services.user_creation_service.uuid.uuid4",
        return_value="generated-uuid",
    ):

        result = service.create_user(
            first_name="Leila",
            last_name="El",
            email="Leila@example.com",
            password="Password123!",
            role=UserRole.CLIENT,
            is_verified=False,
            is_active=False,
            accepted_cgu=False,
        )

    assert result.is_verified is False
    assert result.is_active is False
    assert result.accepted_cgu is False


def test_create_user_hashes_password():
    service, user_repository = create_service()

    user_repository.save.side_effect = (
        lambda user: user
    )
    user_repository.get_by_email.return_value = None
    with patch(
        "modules.auth.application.services.user_creation_service.hash_password",
        return_value="hashed-password",
    ) as mock_hash_password, patch(
        "modules.auth.application.services.user_creation_service.uuid.uuid4",
        return_value="generated-uuid",
    ):

        result = service.create_user(
            first_name="Leila",
            last_name="El",
            email="Leila@example.com",
            password="PlainPassword123!",
            role=UserRole.CLIENT,
        )

    mock_hash_password.assert_called_once_with(
        "PlainPassword123!"
    )

    assert result.password == "hashed-password"