from datetime import datetime, timezone, timedelta
import logging

from core.security.password import hash_password

from modules.auth.domain.exceptions import (
    InvalidActivationToken,
    CguNotAccepted,
)

from modules.auth.domain.entities.refresh_token import RefreshToken
from modules.auth.application.dtos.activate_account_dto import (
    ActivateAccountDTO,
)
from modules.auth.application.results.activate_account_result import (
    ActivateAccountResult,
)

from modules.applications.domain.enums import EventType


logger = logging.getLogger(__name__)


class ActivateAccountUseCase:

    def __init__(
        self,
        validator,
        activation_token_repository,
        user_repository,
        refresh_repository,
        jwt_service,
        event_service,
        uow,
    ):
        self.validator = validator
        self.activation_token_repository = (
            activation_token_repository
        )
        self.user_repository = user_repository
        self.refresh_repository = refresh_repository
        self.jwt_service = jwt_service
        self.event_service = event_service
        self.uow = uow

    def execute(
        self,
        dto: ActivateAccountDTO,
    ) -> ActivateAccountResult:

        user = None

        try:

            # =========================
            # VALIDATE TOKEN
            # =========================

            activation = (
                self.validator
                .get_activation(dto.token)
            )

            self.validator.validate_for_activation(
                activation
            )

            # =========================
            # CGU
            # =========================

            if not dto.accepted_cgu:
                raise CguNotAccepted()

            # =========================
            # USER
            # =========================

            user = (
                self.user_repository
                .get_by_id(activation.user_id)
            )

            if not user:
                raise InvalidActivationToken()

            # =========================
            # ACTIVATE USER
            # =========================

            user.activate(
                hashed_password=hash_password(
                    dto.password
                )
            )

            # =========================
            # CONSUME TOKEN
            # =========================

            now = datetime.now(timezone.utc)

            activation.consume(now)

            # =========================
            # SAVE USER + TOKEN
            # =========================

            self.user_repository.update(user)

            self.activation_token_repository.update(
                activation
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.USER_ACCOUNT_ACTIVATED,
                message="Compte utilisateur activé",
                user_id=user.id,
                event_metadata={
                    "email": user.email,
                },
            )

            # =========================
            # CREATE JWT
            # =========================

            access_token = (
                self.jwt_service.create_access_token(
                    user_id=user.id,
                    role=user.role,
                )
            )

            refresh_token = (
                self.jwt_service.create_refresh_token(
                    user_id=user.id,
                    role=user.role,
                )
            )

            payload = self.jwt_service.decode(
                refresh_token
            )

            refresh_entity = RefreshToken(
                id=payload["jti"],
                user_id=user.id,
                role=user.role,
                jti=payload["jti"],
                expires_at=(
                    now + timedelta(days=7)
                ),
                created_at=now,
                revoked=False,
            )

            self.refresh_repository.save(
                refresh_entity
            )

            # =========================
            # COMMIT
            # =========================

            self.uow.commit()

            logger.info(
                "Compte utilisateur activé",
                extra={
                    "user_id": user.id,
                },
            )

            return ActivateAccountResult(
                access_token=access_token,
                refresh_token=refresh_token,
                redirect=(
                    f"/quotes/{activation.quote_id}"
                    if activation.quote_id
                    else "/"
                ),
            )

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur activation compte",
                extra={
                    "user_id": (
                        user.id
                        if user
                        else None
                    ),
                },
            )

            raise