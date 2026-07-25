from datetime import datetime, timezone

from modules.auth.domain.exceptions import (
    InvalidActivationToken,
    CguNotAccepted
)

from core.security.password import hash_password
from datetime import datetime, timezone, timedelta

from modules.auth.api.schemas import ActivateAccountRequest, ActivateAccountResponse
from modules.auth.domain.entities.refresh_token import RefreshTokenEntity

class ActivateAccountUseCase:


    def __init__(
        self,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
    ):

        self.validator = validator

        self.activation_token_repository = (
            activation_token_repository
        )

        self.user_repository = (
            user_repository
        )
        self.refresh_repository = refresh_repository

        self.jwt_service = jwt_service



    def execute(
        self,
        request: ActivateAccountRequest,
    ):


        # =========================
        # VALIDATE TOKEN
        # =========================

        activation = (
    self.validator.get_activation(request.token)
)


        self.validator.validate_for_activation(
    activation
)


        # =========================
        # CGU
        # =========================

        if not request.accepted_cgu:

            raise CguNotAccepted()


        # =========================
        # USER
        # =========================

        user = (
            self.user_repository.get_by_id(
                activation.user_id
            )
        )


        if user is None:

            raise InvalidActivationToken()


        # =========================
        # ACTIVATE USER
        # =========================

        user.activate(
            hashed_password=hash_password(
                request.password
            )
        )


        # =========================
        # CONSUME TOKEN
        # =========================

        activation.consume(
            datetime.now(
                timezone.utc
            )
        )


        # =========================
        # SAVE
        # =========================

        self.user_repository.update(
            user
        )

        self.activation_token_repository.update(
            activation
        )


        # =========================
        # JWT
        # =========================

        access_token = (
            self.jwt_service.create_access_token(
                user_id=user.id,
                role=user.role.value,
            )
        )

        refresh_token = (
            self.jwt_service.create_refresh_token(
                user_id=user.id,
                role=user.role.value,
            )
        )
        payload = self.jwt_service.decode(refresh_token)
        jti = payload["jti"]
        now = datetime.now(timezone.utc)

        # =========================
        # 3. SAVE SESSION (JTI BASED)
        # =========================
        refresh_token_entity = RefreshTokenEntity(
            id=jti,
            user_id=user.id,
            role=user.role,
            jti=jti,
            expires_at=now + timedelta(days=7),
            created_at=now,
            revoked=False
        )
        self.refresh_repository.save(refresh_token_entity)

        # =========================
        # RESPONSE
        # =========================

        return ActivateAccountResponse(

            message="Compte activé avec succès.",

            access_token=access_token,

            refresh_token=refresh_token,

            redirect=(
                f"/quotes/{activation.quote_id}"
                if activation.quote_id
                else "/"
            ),
        )