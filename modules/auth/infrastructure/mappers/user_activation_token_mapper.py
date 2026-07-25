from modules.auth.domain.entities.user_activation_token import UserActivationToken
from modules.auth.infrastructure.db.user_activation_token_model import UserActivationTokenModel

class UserActivationTokenMapper:

    # =====================================
    # DOMAIN -> MODEL
    # =====================================

    @staticmethod
    def to_model(
        token: UserActivationToken,
    ) -> UserActivationTokenModel:

        return UserActivationTokenModel(

            id=token.id,

            user_id=token.user_id,

            quote_id=token.quote_id,

            token_hash=token.token_hash,

            expires_at=token.expires_at,

            used_at=token.used_at,

            created_at=token.created_at,
        )

    # =====================================
    # MODEL -> DOMAIN
    # =====================================

    @staticmethod
    def to_domain(
        model: UserActivationTokenModel,
    ) -> UserActivationToken:

        return UserActivationToken(

            id=model.id,

            user_id=model.user_id,

            quote_id=model.quote_id,

            token_hash=model.token_hash,

            expires_at=model.expires_at,

            used_at=model.used_at,

            created_at=model.created_at,
        )

    # =====================================
    # UPDATE MODEL
    # =====================================

    @staticmethod
    def update_model(
        model: UserActivationTokenModel,
        token: UserActivationToken,
    ) -> None:

        model.used_at = token.used_at
        model.expires_at = token.expires_at