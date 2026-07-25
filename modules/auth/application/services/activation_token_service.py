import uuid
import secrets
import hashlib

from datetime import (
    datetime,
    timedelta,
    timezone,
)

from modules.auth.infrastructure.db.user_activation_token_model import UserActivationTokenModel


class ActivationTokenService:


    def __init__(
        self,
        repository
    ):

        self.repository = repository



    def create(
        self,
        user_id,
        quote_id: str | None = None,
    ):

        raw_token = (
            secrets.token_urlsafe(48)
        )


        token_hash = hashlib.sha256(
            raw_token.encode()
        ).hexdigest()



        model = UserActivationTokenModel(

            id=str(uuid.uuid4()),

            user_id=user_id,
                    
            quote_id=quote_id,

            token_hash=token_hash,

            expires_at=(
                datetime.now(timezone.utc)
                +
                timedelta(hours=48)
            )
        )


        self.repository.save(
            model
        )

        print(raw_token)
        return raw_token