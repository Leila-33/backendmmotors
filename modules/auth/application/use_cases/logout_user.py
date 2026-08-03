from modules.auth.api.schemas import LogoutResponse

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
        try:

            payload = self.jwt_service.decode(
                refresh_token
            )

            jti = payload["jti"]

            self.refresh_repository.revoke_by_jti(
                jti
            )

            self.uow.commit()

            return LogoutResponse(
                message="Logged out"
            )
        except Exception:
            self.uow.rollback()
            raise