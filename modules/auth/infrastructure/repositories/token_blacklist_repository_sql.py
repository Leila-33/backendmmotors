from sqlalchemy.orm import Session
from modules.auth.infrastructure.db.token_blacklist_model import TokenBlacklistModel
from modules.auth.domain.entities.token_blacklist import TokenBlacklist
from modules.auth.domain.repositories.token_blacklist_repository import (
    TokenBlacklistRepository,
)
from modules.auth.infrastructure.mappers.token_blacklist_mapper import (
    TokenBlacklistMapper,
)


class BlacklistRepositorySQL(
    TokenBlacklistRepository
):

    def __init__(
        self,
        db: Session
    ):
        self.db = db


    # =========================
    # ADD
    # =========================

    def add(
        self,
        token: TokenBlacklist
    ) -> TokenBlacklist:

        model = TokenBlacklistMapper.to_model(
            token
        )

        self.db.add(model)

        self.db.flush()

        return TokenBlacklistMapper.to_domain(
            model
        )


    # =========================
    # EXISTS
    # =========================

    def exists(
        self,
        token: str
    ) -> bool:

        return (
            self.db.query(TokenBlacklistModel)
            .filter(
                TokenBlacklistModel.token == token
            )
            .first()
            is not None
        )