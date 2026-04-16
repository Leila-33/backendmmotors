from modules.clients.domain.entities.user import User
from modules.clients.domain.repositories.user_repository import UserRepository
from modules.clients.infrastructure.db.models import UserModel
from infrastructure.db.session import SessionLocal
class UserRepositorySQL(UserRepository):

    def get_by_email(self, email: str):
        db = SessionLocal()
        u = db.query(UserModel).filter(UserModel.email == email).first()

        if not u:
            return None

        return User(
            id=u.id,
            first_name=u.first_name,
            last_name=u.last_name,
            email=u.email,
            password=u.password,
            accepted_cgu=u.accepted_cgu
        )

    def save(self, user: User):
        db = SessionLocal()

        model = UserModel(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            accepted_cgu=user.accepted_cgu
        )

        db.add(model)
        db.commit()