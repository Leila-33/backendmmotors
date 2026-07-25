import uuid
import secrets
from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from core.security.password import hash_password


class UserCreationService:


    def __init__(
        self,
        user_repository,
    ):
        self.user_repository = (
            user_repository
        )


    def create_client(
    self,
    first_name,
    last_name,
    email,
):

        user = (
            self.user_repository
            .get_by_email(email)
        )


        if user:

            return user, False

        temp_password = secrets.token_urlsafe(12)

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
            is_active=True,
        )


        self.user_repository.save(user)


        return user, True