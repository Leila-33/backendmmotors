from modules.auth.domain.entities.user import User
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.infrastructure.db.user_model import UserModel
from sqlalchemy.orm import Session
from modules.core.enums import UserRole
from modules.auth.infrastructure.mapper.user_mapper import UserMapper
from sqlalchemy import update, or_, desc, asc
from datetime import datetime, timezone

class UserRepositorySQL(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    # =========================
    # GET USER BY EMAIL
    # =========================
    def get_by_email(self, email: str):
        model = self.db.query(UserModel).filter(UserModel.email == email).first()

        if not model:
            return None

        return UserMapper.to_domain(model)

    # =========================
    # GET USER BY ID
    # =========================
    def get_by_id(self, user_id: str):

        model = (
            self.db.query(UserModel)
            .filter(UserModel.id == user_id)
            .first()
        )

        if not model:
            return None

        return UserMapper.to_domain(model)

    # =========================
    # SAVE USER
    # =========================
    def save(self, user: User):

        model = UserMapper.to_model(user)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return UserMapper.to_domain(model)
    
    # =========================
    # UPDATE USER
    # =========================

    def update(self, user: User):

        model = (
            self.db.query(UserModel)
            .filter(UserModel.id == user.id)
            .first()
        )

        if not model:
            return None

        UserMapper.update_model(model, user)

        try:
            self.db.commit()
            self.db.refresh(model)
        except Exception:
            self.db.rollback()
            raise

        return UserMapper.to_domain(model)
    


    def find_all(self, page, limit, search, role, status, sort):

        query = self.db.query(UserModel)

        # =====================
        # SEARCH
        # =====================
        if search:
            search = search.strip()
            query = query.filter(
                or_(
                    UserModel.first_name.ilike(f"%{search}%"),
                    UserModel.last_name.ilike(f"%{search}%"),
                    UserModel.email.ilike(f"%{search}%")
                )
            )

        # =====================
        # ROLE FILTER
        # =====================
        if role:
            role = role.strip().upper()

            if role != "ALL":
                query = query.filter(UserModel.role == role)

        # =====================
        # STATUS FILTER
        # =====================
        if status == "active":
            query = query.filter(UserModel.is_active == True)

        elif status == "inactive":
            query = query.filter(UserModel.is_active == False)

        # =====================
        # SORTING
        # =====================
        if sort == "created_at_desc":
            query = query.order_by(desc(UserModel.created_at))

        elif sort == "created_at_asc":
            query = query.order_by(asc(UserModel.created_at))

        elif sort == "name_asc":
            query = query.order_by(asc(UserModel.first_name))

        elif sort == "name_desc":
            query = query.order_by(desc(UserModel.first_name))

        # =====================
        # COUNT
        # =====================
        total = query.count()

        users = (
            query
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return users, total
    
    def get_active_agents(self):
        return (
            self.db.query(UserModel)
            .filter(UserModel.role == UserRole.SAV_AGENT, UserModel.is_active == True)
            .order_by(UserModel.id.asc())
            .all()
        )
    
    def find_by_ids(self, ids: list[str]):
        return (
            self.db.query(UserModel)
            .filter(UserModel.id.in_(ids))
            .all()
        )


    def archive_many(self, ids: list[str]):

        try:
            self.db.execute(
                update(UserModel)
                .where(UserModel.id.in_(ids))
                .values(
                    is_deleted=True,
                    is_active=False,
                    deleted_at=datetime.now(timezone.utc)
                )
            )

            self.db.commit()

        except Exception:
            self.db.rollback()
            raise