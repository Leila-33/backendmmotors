from modules.auth.domain.exceptions import (
    InvalidActivationToken,
    ActivationTokenExpired,
    ActivationTokenAlreadyUsed
)
from datetime import datetime, timezone


class ActivationTokenValidator:

    """
    Récupère et valide un jeton d'activation en vérifiant son existence,
    son utilisation et sa date d'expiration.
    """
    def __init__(
        self,
        activation_token_repository,
    ):
        self.activation_token_repository = (
            activation_token_repository
        )

    def get_activation(
        self,
        token: str,
    ):

        activation = (
            self.activation_token_repository
            .find_by_token(token)
        )

        if activation is None:
            raise InvalidActivationToken()

        return activation
    

    def validate_for_activation(
        self,
        activation,
    ):

        now = datetime.now(
            timezone.utc
        )

        if activation.is_used():

            raise ActivationTokenAlreadyUsed()


        if activation.is_expired(now):

            raise ActivationTokenExpired()


        return activation