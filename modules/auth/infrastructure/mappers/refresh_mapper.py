from modules.auth.domain.entities.refresh_token import RefreshToken
from modules.auth.infrastructure.db.refresh_token_model import (
    RefreshTokenModel,
)


class RefreshTokenMapper:

    # =========================
    # MODEL -> DOMAIN
    # =========================
    @staticmethod
    def to_domain(
        model: RefreshTokenModel
    ) -> RefreshToken:

        return RefreshToken(

            id=model.id,

            user_id=model.user_id,

            jti=model.jti,

            role=model.role,

            expires_at=model.expires_at,

            revoked=model.revoked,

            created_at=model.created_at,

            updated_at=model.updated_at,
        )

    # =========================
    # DOMAIN -> MODEL
    # =========================
    @staticmethod
    def to_model(
        token: RefreshToken
    ) -> RefreshTokenModel:

        return RefreshTokenModel(

            id=token.id,

            user_id=token.user_id,

            jti=token.jti,

            role=token.role,

            expires_at=token.expires_at,

            revoked=token.revoked,

            created_at=token.created_at,

            updated_at=token.updated_at,
        )

    # =========================
    # UPDATE MODEL
    # =========================
    @staticmethod
    def update_model(
        model: RefreshTokenModel,
        token: RefreshToken
    ):

        model.jti = token.jti

        model.role = token.role

        model.expires_at = token.expires_at

        model.revoked = token.revoked

        model.updated_at = token.updated_at