from modules.auth.api.schemas import RegisterResponse

class RegisterUser:

    def __init__(
        self,
        user_creation_service,
        jwt_service,
        email_service,
        uow
    ):

        self.user_creation_service = (
            user_creation_service
        )

        self.jwt = jwt_service

        self.email_service = email_service

        self.uow = uow


    def execute(
        self,
        data
    ):

        try:

            user = (
                self.user_creation_service
                .create_client(
                    first_name=data.first_name,
                    last_name=data.last_name,
                    email=data.email,
                    password=data.password,
                    accepted_cgu=data.accepted_cgu
                )
            )


            token = (
                self.jwt
                .create_email_token(
                    user.id
                )
            )


            self.email_service.send_verification_email(
                email=user.email,
                token=token,
            )


            self.uow.commit()


            return RegisterResponse(
                message="Utilisateur créé avec succès."
            )


        except Exception:

            self.uow.rollback()

            raise