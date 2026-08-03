from modules.auth.domain.exceptions import TokenInvalid
from modules.auth.api.schemas import VerifyEmailResponse

class VerifyEmail:

    def __init__(
        self,
        user_repo,
        jwt_service,
        uow
    ):
        self.user_repo = user_repo
        self.jwt = jwt_service
        self.uow = uow


    # =========================
    # EXECUTE
    # =========================

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


            user_id = payload.get(
                "sub"
            )


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


            self.uow.commit()


            return VerifyEmailResponse(
                message="Email verified"
            )

        except Exception:
            self.uow.rollback()
            raise