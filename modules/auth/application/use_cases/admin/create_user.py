import logging

from modules.applications.domain.enums import EventType
from modules.auth.application.results.admin.create_user_result import (
    CreateUserResult,
)
from modules.auth.application.dtos.admin.create_user_dto import (
    CreateUserDTO,
)
logger = logging.getLogger(__name__)


class CreateUserUseCase:
    """
    Crée un utilisateur à partir des informations fournies par un
    administrateur, puis enregistre l'action dans l'historique
    des événements.
    """
    def __init__(
        self,
        user_creation_service,
        event_service,
        uow,
    ):
        self.user_creation_service = (
            user_creation_service
        )
        self.event_service = event_service
        self.uow = uow

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        dto : CreateUserDTO,
        admin_id: str,
    ) -> CreateUserResult:

        try:

            # =====================================================
            # CREATE USER
            # =====================================================

            user = (
                self.user_creation_service
                .create_user(
                    first_name=dto.first_name,
                    last_name=dto.last_name,
                    email=dto.email,
                    password=dto.password,
                    role=dto.role,
                )
            )

            # =====================================================
            # EVENT
            # =====================================================

            self.event_service.log(
                type=EventType.USER_CREATED,
                message=(
                    "Utilisateur créé par un administrateur"
                ),
                user_id=admin_id,
                event_metadata={
                    "email": user.email,
                    "role": user.role.value,
                },
            )

            # =====================================================
            # COMMIT
            # =====================================================

            self.uow.commit()

            logger.info(
                "Utilisateur créé",
                extra={
                    "user_id": user.id,
                    "role": user.role.value,
                    "admin_id": admin_id,
                },
            )

            # =====================================================
            # RESULT
            # =====================================================

            return CreateUserResult(
                id=user.id,
                email=user.email,
                role=user.role,
            )

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur création utilisateur",
                extra={
                    "admin_id": admin_id,
                },
            )

            raise