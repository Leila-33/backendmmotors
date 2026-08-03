from modules.auth.api.schemas import CreateUserResponse

class CreateUserUseCase:

    def __init__(
        self,
        user_creation_service,
        uow,
    ):
        self.user_creation_service = (
            user_creation_service
        )

        self.uow = uow

    # =====================
    # EXECUTE
    # =====================
    def execute(
        self,
        payload,
    ) -> CreateUserResponse:

        try:

            user = (
                self.user_creation_service
                .create_user(
                    first_name=payload.first_name,
                    last_name=payload.last_name,
                    email=payload.email,
                    password=payload.password,
                    role=payload.role,
                )
            )

            self.uow.commit()

            return CreateUserResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                message="Utilisateur créé avec succès",
            )

        except Exception:

            self.uow.rollback()

            raise