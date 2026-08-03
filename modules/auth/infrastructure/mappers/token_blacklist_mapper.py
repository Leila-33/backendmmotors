from modules.auth.domain.entities.token_blacklist import TokenBlacklist
from modules.auth.infrastructure.db.token_blacklist_model import (
    TokenBlacklistModel,
)


class TokenBlacklistMapper:


    # =========================
    # MODEL -> DOMAIN
    # =========================

    @staticmethod
    def to_domain(
        model: TokenBlacklistModel
    ) -> TokenBlacklist:

        return TokenBlacklist(

            id=model.id,

            token=model.token,

            created_at=model.created_at,
        )


    # =========================
    # DOMAIN -> MODEL
    # =========================

    @staticmethod
    def to_model(
        blacklist: TokenBlacklist
    ) -> TokenBlacklistModel:

        return TokenBlacklistModel(

            id=blacklist.id,

            token=blacklist.token,

            created_at=blacklist.created_at,
        )


    # =========================
    # UPDATE MODEL
    # =========================

    @staticmethod
    def update_model(
        model: TokenBlacklistModel,
        blacklist: TokenBlacklist
    ):

        model.token = (
            blacklist.token
        )

        model.created_at = (
            blacklist.created_at
        )