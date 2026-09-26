import uuid
from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from core.security.password import hash_password
from modules.auth.domain.exceptions import EmailAlreadyExists
import secrets

class UserCreationService:

    def __init__(
        self,
        user_repository,
    ):
        self.user_repository = user_repository


    # =====================================
    # REGISTER USER
    # =====================================

    def create_client(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        accepted_cgu: bool = False
    ):

        existing = (
            self.user_repository
            .get_by_email(email)
        )

        if existing:
            raise EmailAlreadyExists()


        user = User(
            id=str(uuid.uuid4()),

            first_name=first_name,

            last_name=last_name,

            email=email,

            password=hash_password(password),

            role=UserRole.CLIENT,

            is_verified=False,

            is_active=True,

            accepted_cgu=accepted_cgu,
        )


        return (
            self.user_repository
            .save(user)
        )


    # =====================================
    # CRM / LEAD CREATION
    # =====================================

    def create_client_without_password(
        self,
        first_name: str,
        last_name: str,
        email: str,
    ):

        existing = (
            self.user_repository
            .get_by_email(email)
        )


        if existing:
            return existing, False


        temp_password = (
            secrets.token_urlsafe(12)
        )


        user = User(
            id=str(uuid.uuid4()),

            first_name=first_name,

            last_name=last_name,

            email=email,

            password=hash_password(
                temp_password
            ),

            role=UserRole.CLIENT,

            is_verified=False,

            is_active=False,

            accepted_cgu=False,
        )


        self.user_repository.save(
            user
        )

        return user, True

    # =====================================
    # CREATE USER (ADMIN)
    # =====================================

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        role: UserRole,
        is_verified: bool = True,
        is_active: bool = True,
        accepted_cgu: bool = True,
    ) -> User:

        existing = (
            self.user_repository
            .get_by_email(email)
        )

        if existing:
            raise EmailAlreadyExists()

        user = User(
            id=str(uuid.uuid4()),
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hash_password(password),
            role=role,
            is_verified=is_verified,
            is_active=is_active,
            accepted_cgu=accepted_cgu,
        )

        return self.user_repository.save(user)