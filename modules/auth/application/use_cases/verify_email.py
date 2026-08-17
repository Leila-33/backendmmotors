from modules.auth.domain.exceptions import TokenInvalid
from modules.auth.application.results.verify_email_result import VerifyEmailResult
from modules.auth.api.schemas import VerifyEmailResponse
from modules.applications.domain.enums import EventType
import logging

logger = logging.getLogger(__name__)




class VerifyEmailUseCase:

    def __init__(
        self,
        user_repo,
        jwt_service,
        event_service,
        uow
    ):
        self.user_repo = user_repo
        self.jwt = jwt_service
        self.event_service = event_service
        self.uow = uow


    def execute(
        self,
        token: str
    ) -> VerifyEmailResult:

        payload = None

        try:

            # =========================
            # DECODE TOKEN
            # =========================

            payload = (
                self.jwt.decode(token)
            )


            if (
                payload.get("type")
                != "email_verification"
            ):
                raise TokenInvalid()


            user_id = payload.get("sub")


            if not user_id:
                raise TokenInvalid()



            # =========================
            # USER
            # =========================

            user = (
                self.user_repo
                .get_by_id(user_id)
            )


            if not user:
                raise TokenInvalid()



            # =========================
            # IDEMPOTENCE
            # =========================

            if user.is_verified:

                logger.info(
                    "Email déjà vérifié",
                    extra={
                        "user_id": user.id
                    }
                )

                return VerifyEmailResponse(
                    message="Email déjà vérifié"
                )



            # =========================
            # VERIFY
            # =========================

            user.is_verified = True


            self.user_repo.update(
                user
            )



            # =========================
            # EVENT
            # =========================

            self.event_service.log(

                type=EventType.USER_EMAIL_VERIFIED,

                message="Email utilisateur vérifié",

                user_id=user.id,

                event_metadata={
                    "action": "email_verified"
                }
            )



            self.uow.commit()



            logger.info(
                "Email utilisateur vérifié",
                extra={
                    "user_id": user.id
                }
            )


            return VerifyEmailResult(
                message="Email vérifié"
            )



        except TokenInvalid:

            logger.warning(
                "Tentative validation email avec token invalide",
                extra={
                    "token_type": (
                        payload.get("type")
                        if payload
                        else None
                    )
                }
            )

            raise



        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur technique vérification email",
                extra={
                    "user_id": (
                        payload.get("sub")
                        if payload
                        else None
                    )
                }
            )

            raise