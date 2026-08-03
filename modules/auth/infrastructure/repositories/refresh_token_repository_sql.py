from modules.auth.infrastructure.db.refresh_token_model import RefreshTokenModel
from modules.auth.domain.entities.refresh_token import RefreshToken


from datetime import datetime, timezone

from sqlalchemy.orm import Session

from modules.auth.domain.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from modules.auth.infrastructure.mappers.refresh_mapper import (
    RefreshTokenMapper,
)


class RefreshTokenRepositorySQL(
    RefreshTokenRepository
):

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    # =========================
    # SAVE
    # =========================
    def save(
        self,
        token: RefreshToken
    ) -> RefreshToken:

        model = RefreshTokenMapper.to_model(
            token
        )

        self.db.add(model)

        self.db.flush()

        return RefreshTokenMapper.to_domain(
            model
        )

    # =========================
    # UPDATE
    # =========================
    def update(
        self,
        token: RefreshToken
    ) -> RefreshToken | None:

        model = (
            self.db.query(RefreshTokenModel)
            .filter(
                RefreshTokenModel.id == token.id
            )
            .first()
        )

        if not model:
            return None

        RefreshTokenMapper.update_model(
            model,
            token
        )

        self.db.flush()

        return RefreshTokenMapper.to_domain(
            model
        )

    # =========================
    # FIND BY JTI
    # =========================
    def find_by_jti(
        self,
        jti: str
    ) -> RefreshToken | None:

        model = (
            self.db.query(RefreshTokenModel)
            .filter(
                RefreshTokenModel.jti == jti
            )
            .first()
        )

        if not model:
            return None

        return RefreshTokenMapper.to_domain(
            model
        )

    # =========================
    # FIND BY USER
    # =========================
    def find_by_user(
        self,
        user_id: str
    ) -> list[RefreshToken]:

        models = (
            self.db.query(RefreshTokenModel)
            .filter(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked.is_(False)
            )
            .all()
        )

        return [
            RefreshTokenMapper.to_domain(model)
            for model in models
        ]

    # =========================
    # REVOKE BY JTI
    # =========================
    def revoke_by_jti(
        self,
        jti: str
    ):

        token = self.find_by_jti(jti)

        if not token:
            return

        token.revoked = True
        token.updated_at = datetime.now(
            timezone.utc
        )

        self.update(token)

    # =========================
    # REVOKE ALL USER SESSIONS
    # =========================
    def revoke_all_by_user(
        self,
        user_id: str
    ):

        models = (
            self.db.query(RefreshTokenModel)
            .filter(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked.is_(False)
            )
            .all()
        )

        now = datetime.now(timezone.utc)

        for model in models:

            model.revoked = True
            model.updated_at = now

        self.db.flush()