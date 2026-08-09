from modules.auth.api.schemas import RegisterResponse
from modules.applications.domain.enums import EventType
import logging

logger = logging.getLogger(__name__)

class RegisterUser:

    def __init__(
        self,
        user_creation_service,
        jwt_service,
        email_service,
        event_service,
        uow
    ):

        self.user_creation_service = user_creation_service

        self.jwt = jwt_service

        self.email_service = email_service

        self.event_service = event_service

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


            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.USER_REGISTERED,
                message="Nouvel utilisateur inscrit",
                user_id=user.id,
                event_metadata={
                    "email": user.email
                }
            )


            token = (
                self.jwt
                .create_email_token(
                    user.id
                )
            )

            self.uow.commit()
            
            logger.info(
                "Nouvelle inscription utilisateur",
                extra={
                    "user_id": user.id,
                    "email": user.email,
                }
            )
            
            self.email_service.send_verification_email(
                email=user.email,
                token=token,
            )


            return RegisterResponse(
                message="Utilisateur créé avec succès."
            )


        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur lors de l'inscription utilisateur",
                extra={
                    "email": data.email
                }
            )

            raise