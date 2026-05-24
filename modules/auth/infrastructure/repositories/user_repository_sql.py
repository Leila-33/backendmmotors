from modules.auth.domain.entities.user import User
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.infrastructure.db.user_model import UserModel
from sqlalchemy.orm import Session
from sqlalchemy import or_


class UserRepositorySQL(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    # =========================
    # GET USER BY EMAIL
    # =========================
    def get_by_email(self, email: str):
        u = self.db.query(UserModel).filter(UserModel.email == email).first()

        if not u:
            return None

        return User(
            id=u.id,
            first_name=u.first_name,
            last_name=u.last_name,
            email=u.email,
            password=u.password,
            accepted_cgu=u.accepted_cgu,
            is_verified=u.is_verified,
            is_active=u.is_active,
            role=u.role
        )

    # =========================
    # GET USER BY ID
    # =========================
    def get_by_id(self, user_id: str):
        u = self.db.query(UserModel).filter(UserModel.id == user_id).first()

        if not u:
            return None

        return User(
            id=u.id,
            first_name=u.first_name,
            last_name=u.last_name,
            email=u.email,
            password=u.password,
            accepted_cgu=u.accepted_cgu,
            is_verified=u.is_verified,
            is_active=u.is_active,
            role=u.role
        )

    # =========================
    # SAVE USER
    # =========================
    def save(self, user: User):
        model = UserModel(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password=user.password,
            accepted_cgu=user.accepted_cgu,
            is_verified=user.is_verified,
            is_active=user.is_active,
            role=user.role
        )

        try:
            self.db.add(model)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    # =========================
    # UPDATE USER
    # =========================
    def update(self, user: User):
        u = self.db.query(UserModel).filter(UserModel.id == user.id).first()

        if not u:
            return None

        u.first_name = user.first_name
        u.last_name = user.last_name
        u.email = user.email
        u.password = user.password
        u.accepted_cgu = user.accepted_cgu
        u.is_verified = user.is_verified
        u.is_active = user.is_active
        u.role = user.role

        try:
            self.db.commit()
            self.db.refresh(u)
        except Exception:
            self.db.rollback()
            raise

        return User(
            id=u.id,
            first_name=u.first_name,
            last_name=u.last_name,
            email=u.email,
            password=u.password,
            accepted_cgu=u.accepted_cgu,
            is_verified=u.is_verified,
            is_active=u.is_active,
            role=u.role
        )
    
    def find_all(self, page, limit, search, role):

        query = self.db.query(UserModel)

        # =========================
        # SEARCH
        # =========================
        if search:
            search = search.strip()

            query = query.filter(
                or_(
                    UserModel.first_name.ilike(f"%{search}%"),
                    UserModel.last_name.ilike(f"%{search}%"),
                    UserModel.email.ilike(f"%{search}%")
                )
            )

        # =========================
        # ROLE FILTER
        # =========================
        if role and role != "all":
            query = query.filter(UserModel.role == role)

        total = query.count()

        users = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return users, total