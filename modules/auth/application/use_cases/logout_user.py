from modules.auth.api.schemas import LogoutResponse
from modules.auth.domain.exceptions import InvalidRefreshToken
import logging

logger = logging.getLogger(__name__)


class LogoutUser:

    def __init__(
        self,
        refresh_repository,
        jwt_service,
        uow
    ):
        self.refresh_repository = refresh_repository
        self.jwt_service = jwt_service
        self.uow = uow


    # =========================
    # EXECUTE
    # =========================

    def execute(
        self,
        refresh_token: str
    ) -> LogoutResponse:

        payload = None

        try:

            # =========================
            # DECODE TOKEN
            # =========================

            payload = (
                self.jwt_service
                .decode(refresh_token)
            )


            jti = payload.get(
                "jti"
            )

            user_id = payload.get(
                "sub"
            )


            if not jti:

                logger.warning(
                    "Logout impossible : jti absent",
                    extra={
                        "user_id": user_id,
                    }
                )

                raise InvalidRefreshToken()



            # =========================
            # REVOKE TOKEN
            # =========================

            self.refresh_repository.revoke_by_jti(
                jti
            )


            # =========================
            # COMMIT
            # =========================

            self.uow.commit()



            # =========================
            # LOG SUCCESS
            # =========================

            logger.info(
                "Utilisateur déconnecté",
                extra={
                    "user_id": user_id,
                    "refresh_token_jti": jti,
                }
            )


            return LogoutResponse(
                message="Logged out"
            )


        # =========================
        # TOKEN INVALID
        # =========================

        except InvalidRefreshToken:

            logger.warning(
                "Tentative logout avec refresh token invalide",
                extra={
                    "user_id": (
                        payload.get("sub")
                        if payload
                        else None
                    )
                }
            )

            raise



        # =========================
        # ERREUR TECHNIQUE
        # =========================

        except Exception:


            self.uow.rollback()


            logger.exception(
                "Erreur technique déconnexion utilisateur",
                extra={
                    "user_id": (
                        payload.get("sub")
                        if payload
                        else None
                    )
                }
            )


            raise