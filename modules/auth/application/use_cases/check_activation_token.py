from modules.auth.api.schemas import CheckActivationTokenResponse


from modules.auth.domain.exceptions import (
    InvalidActivationToken
)
from datetime import datetime, timezone


class CheckActivationTokenUseCase:


    def __init__(
        self,
        validator,
        user_repository,
    ):

        self.validator = validator
    

        self.user_repository = user_repository



    def execute(
        self,
        token: str,
    ) -> CheckActivationTokenResponse:


        # =========================
        # FIND TOKEN
        # =========================

        activation = (
        self.validator.get_activation(token)
    )


        # =========================
        # FIND USER
        # =========================

        user = (
            self.user_repository
            .get_by_id(
                activation.user_id
            )
        )


        if not user:

            raise InvalidActivationToken()

        now = datetime.now(
            timezone.utc
        )

        # =========================
        # RESPONSE
        # =========================

        return CheckActivationTokenResponse(

            first_name=user.first_name,

            email=user.email,

            already_verified=user.is_verified,
            expired=activation.is_expired(now)

        )