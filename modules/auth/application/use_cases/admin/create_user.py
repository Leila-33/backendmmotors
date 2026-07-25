from modules.auth.domain.exceptions import EmailAlreadyExists
from modules.auth.domain.enums import UserRole
from modules.auth.domain.entities.user import User
from uuid import uuid4
from core.security.password import hash_password

class CreateUserUseCase:

    def __init__(self, user_repo):
        self.user_repo = user_repo

    def execute(self, payload):
        # =====================
        # EMAIL CHECK
        # =====================
        if self.user_repo.get_by_email(payload.email):
            raise EmailAlreadyExists

        # =====================
        # ROLE VALIDATION (IMPORTANT)
        # =====================
        role = UserRole(payload.role)

        # =====================
        # CREATE USER
        # =====================
        user = User(
            id=str(uuid4()),
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            password=hash_password(payload.password),
            role=role,
            is_active=True,
            is_verified=True,
            accepted_cgu=True,
        )

        self.user_repo.save(user)

        return {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }