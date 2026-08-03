import hashlib
from sqlalchemy.orm import Session
from modules.auth.domain.repositories.user_activation_token_repository import UserActivationTokenRepository
from modules.auth.infrastructure.db.user_activation_token_model import UserActivationTokenModel
from modules.auth.infrastructure.mappers.user_activation_token_mapper import UserActivationTokenMapper
from modules.auth.domain.entities.user_activation_token import UserActivationToken




class SQLActivationTokenRepository(
    UserActivationTokenRepository
):

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    # =====================================
    # SAVE
    # =====================================

    def save(
        self,
        token: UserActivationToken,
    ) -> UserActivationToken:

        model = UserActivationTokenMapper.to_model(
            token
        )

        self.db.add(model)

        self.db.flush()

        return UserActivationTokenMapper.to_domain(
            model
        )

    # =====================================
    # FIND BY TOKEN
    # =====================================

    def find_by_token(
        self,
        token: str,
    ) -> UserActivationToken | None:

        token_hash = hashlib.sha256(
            token.encode()
        ).hexdigest()

        model = (
            self.db.query(
                UserActivationTokenModel
            )
            .filter(
                UserActivationTokenModel.token_hash
                == token_hash
            )
            .first()
        )

        if not model:
            return None

        return UserActivationTokenMapper.to_domain(
            model
        )

    # =====================================
    # UPDATE
    # =====================================

    def update(
        self,
        token: UserActivationToken,
    ) -> UserActivationToken | None:

        model = (
            self.db.query(
                UserActivationTokenModel
            )
            .filter(
                UserActivationTokenModel.id == token.id
            )
            .first()
        )

        if not model:
            return None

        UserActivationTokenMapper.update_model(
            model,
            token
        )

        self.db.flush()

        return UserActivationTokenMapper.to_domain(
            model
        )