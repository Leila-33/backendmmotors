from modules.auth.domain.exceptions import TokenInvalid
from modules.auth.api.schemas import VerifyEmailResponse
from modules.applications.domain.enums import EventType

class VerifyEmail:

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
    ) -> VerifyEmailResponse:

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
            # GET USER
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

                return VerifyEmailResponse(
                    message="Email already verified"
                )


            # =========================
            # VERIFY USER
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
                message="Compte utilisateur activé",
                user_id=user.id,
                event_metadata={
                    "email": user.email
                }
            )


            self.uow.commit()


            return VerifyEmailResponse(
                message="Email verified"
            )


        except Exception:

            self.uow.rollback()

            raise