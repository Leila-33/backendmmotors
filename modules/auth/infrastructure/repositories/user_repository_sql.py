from sqlalchemy import or_, asc, desc, select
from sqlalchemy.orm import Session

from modules.auth.domain.entities.user import User
from modules.auth.domain.enums import UserRole
from modules.auth.domain.repositories.user_repository import UserRepository

from modules.auth.infrastructure.db.user_model import UserModel
from modules.auth.infrastructure.mappers.user_mapper import UserMapper


class UserRepositorySQL(UserRepository):


    def __init__(
        self,
        db: Session
    ):

        self.db = db



    # =========================
    # GET BY EMAIL
    # =========================

    def get_by_email(
        self,
        email: str
    ) -> User | None:


        model = (
            self.db.query(UserModel)
            .filter(
                UserModel.email == email
            )
            .first()
        )


        if not model:
            return None


        return UserMapper.to_domain(model)



    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        user_id: str
    ) -> User | None:


        model = (
            self.db.query(UserModel)
            .filter(
                UserModel.id == user_id
            )
            .first()
        )


        if not model:
            return None


        return UserMapper.to_domain(model)
    

    # =========================
    # SAVE
    # =========================

    def save(
        self,
        user: User
    ) -> User:


        model = UserMapper.to_model(user)


        self.db.add(model)

        self.db.flush()

        return UserMapper.to_domain(model)



    # =========================
    # UPDATE
    # =========================

    def update(
        self,
        user: User
    ) -> User | None:


        model = (
            self.db.query(UserModel)
            .filter(
                UserModel.id == user.id
            )
            .first()
        )


        if not model:
            return None


        UserMapper.update_model(
            model,
            user
        )


        self.db.flush()


        return UserMapper.to_domain(model)



    # =========================
    # FIND ALL
    # =========================

    def find_all(
        self,
        page: int,
        limit: int,
        search: str | None = None,
        role: str | None = None,
        status: str | None = None,
        sort: str | None = None,
    ):

        query = self.db.query(
            UserModel
        )


        # =====================
        # SEARCH
        # =====================

        if search:

            search = search.strip()

            query = query.filter(
                or_(
                    UserModel.first_name.ilike(
                        f"%{search}%"
                    ),
                    UserModel.last_name.ilike(
                        f"%{search}%"
                    ),
                    UserModel.email.ilike(
                        f"%{search}%"
                    )
                )
            )


        # =====================
        # ROLE
        # =====================

        if role:

            role = role.upper()

            if role != "ALL":

                query = query.filter(
                    UserModel.role == role
                )


        # =====================
        # STATUS
        # =====================

        if status == "active":

            query = query.filter(
                UserModel.is_deleted.is_(False),
                UserModel.is_active.is_(True),
                UserModel.is_verified.is_(True)
            )


        elif status == "pending":

            query = query.filter(
                UserModel.is_deleted.is_(False),
                UserModel.is_active.is_(True),
                UserModel.is_verified.is_(False)
            )


        elif status == "inactive":

            query = query.filter(
                UserModel.is_deleted.is_(False),
                UserModel.is_active.is_(False)
            )


        elif status == "archived":

            query = query.filter(
                UserModel.is_deleted.is_(True)
            )


        else:

            query = query.filter(
                UserModel.is_deleted.is_(False)
            )


        # =====================
        # SORT
        # =====================

        if sort == "created_at_desc":

            query = query.order_by(
                desc(UserModel.created_at)
            )


        elif sort == "created_at_asc":

            query = query.order_by(
                asc(UserModel.created_at)
            )


        elif sort == "name_asc":

            query = query.order_by(
                asc(UserModel.first_name)
            )


        elif sort == "name_desc":

            query = query.order_by(
                desc(UserModel.first_name)
            )


        else:

            query = query.order_by(
                desc(UserModel.created_at)
            )


        # =====================
        # COUNT
        # =====================

        total = query.count()


        # =====================
        # PAGINATION
        # =====================

        page = max(page, 1)

        limit = min(
            max(limit, 1),
            100
        )


        models = (
            query
            .offset(
                (page - 1) * limit
            )
            .limit(limit)
            .all()
        )


        # =====================
        # MAPPER
        # =====================

        users = [
            UserMapper.to_domain(model)
            for model in models
        ]


        return users, total


    # =========================
    # FIND BY IDS
    # =========================

    def find_by_ids(
        self,
        ids: list[str]
    ):


        models = (
            self.db.query(UserModel)
            .filter(
                UserModel.id.in_(ids)
            )
            .all()
        )


        return [
            UserMapper.to_domain(model)
            for model in models
        ]

    # =========================
    # GET BY ROLE
    # =========================

    def get_by_role(
        self,
        role: UserRole,
    ) -> list[User]:
        """
        Retourne les utilisateurs actifs correspondant au rôle demandé.
        """

        models = (
            self.db.query(UserModel)
            .filter(
                UserModel.role == role,
                UserModel.is_active.is_(True),
                UserModel.is_deleted.is_(False),
            )
            .order_by(
                UserModel.id.asc(),
            )
            .all()
        )

        return [
            UserMapper.to_domain(model)
            for model in models
        ]