import logging
from datetime import datetime, timezone

from core.security.password import verify_password

from modules.auth.application.dtos.login_user_dto import (
    LoginUserDTO,
)
from modules.auth.application.results.login_user_result import (
    LoginUserResult,
)
from modules.auth.domain.entities.refresh_token import (
    RefreshToken,
)
from modules.auth.domain.exceptions import (
    InvalidCredentials,
    AccountDisabled,
    EmailNotVerified,
    AccountDeleted,
)

logger = logging.getLogger(__name__)


class LoginUserUseCase:

    def __init__(
        self,
        user_repo,
        jwt_service,
        refresh_repo,
        uow,
    ):
        self.user_repo = user_repo
        self.jwt = jwt_service
        self.refresh_repo = refresh_repo
        self.uow = uow

    # =========================
    # EXECUTE
    # =========================

    def execute(
        self,
        data: LoginUserDTO,
    ) -> LoginUserResult:

        try:

            # =========================
            # GET USER
            # =========================

            user = (
                self.user_repo
                .get_by_email(data.email)
            )

            if (
                not user
                or not verify_password(
                    data.password,
                    user.password,
                )
            ):
                logger.warning(
                    "Échec tentative connexion",
                    extra={
                        "email": data.email,
                    },
                )

                raise InvalidCredentials()

            # =========================
            # ACCOUNT STATUS
            # =========================

            if user.is_deleted:
                raise AccountDeleted()

            if not user.is_active:
                raise AccountDisabled()

            if not user.is_verified:
                raise EmailNotVerified()

            # =========================
            # CREATE ACCESS TOKEN
            # =========================

            access_token = (
                self.jwt.create_access_token(
                    user.id,
                    user.role,
                )
            )

            # =========================
            # CREATE REFRESH TOKEN
            # =========================

            refresh_token_string = (
                self.jwt.create_refresh_token(
                    user.id,
                    user.role,
                )
            )

            payload = self.jwt.decode(
                refresh_token_string
            )

            jti = payload["jti"]

            expires_at = datetime.fromtimestamp(
                payload["exp"],
                tz=timezone.utc,
            )

            # =========================
            # SAVE REFRESH SESSION
            # =========================

            refresh_token = RefreshToken(
                id=jti,
                user_id=user.id,
                role=user.role,
                jti=jti,
                expires_at=expires_at,
                revoked=False,
            )

            self.refresh_repo.save(
                refresh_token
            )

            # =========================
            # COMMIT
            # =========================

            self.uow.commit()

            logger.info(
                "Connexion utilisateur réussie",
                extra={
                    "user_id": user.id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return LoginUserResult(
                access_token=access_token,
                refresh_token=refresh_token_string,
            )

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur authentification utilisateur"
            )

            raise