from modules.auth.domain.entities.user import User
from modules.auth.infrastructure.db.user_model import UserModel


class UserMapper:

    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            password=model.password,
            role=model.role,
            accepted_cgu=model.accepted_cgu,
            is_verified=model.is_verified,
            is_active=model.is_active,
            is_deleted=model.is_deleted,
            created_at=model.created_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(user: User) -> UserModel:
        return UserModel(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            role=user.role,
            accepted_cgu=user.accepted_cgu,
            is_verified=user.is_verified,
            is_active=user.is_active,
            is_deleted=user.is_deleted,
            deleted_at=user.deleted_at,
        )

    @staticmethod
    def update_model(model: UserModel, user: User) -> UserModel:
        model.first_name = user.first_name
        model.last_name = user.last_name
        model.email = user.email
        model.password = user.password
        model.role = user.role
        model.accepted_cgu = user.accepted_cgu
        model.is_verified = user.is_verified
        model.is_active = user.is_active
        model.is_deleted = user.is_deleted
        model.deleted_at = user.deleted_at

        return model