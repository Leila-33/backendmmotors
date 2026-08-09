from modules.auth.domain.exceptions import UserNotFound, Forbidden
from modules.auth.domain.enums import UserRole
from modules.auth.api.schemas import ToggleUserActiveResponse
from modules.applications.domain.enums import EventType
import logging

logger = logging.getLogger(__name__)

class ToggleUserActiveUseCase:


    def __init__(
        self,
        user_repo,
        event_service,
        uow,
    ):

        self.user_repo = user_repo
        self.event_service = event_service
        self.uow = uow

    def execute(
        self,
        user_id: str,
        is_active: bool,
        current_admin
    ) -> ToggleUserActiveResponse:


        try:

            # =====================
            # GET USER
            # =====================

            user = (
                self.user_repo
                .get_by_id(user_id)
            )


            if not user:
                raise UserNotFound()



            # =====================
            # PROTECTION ADMIN
            # =====================

            if user.role == UserRole.ADMIN:

                raise Forbidden(
                    "Impossible de désactiver un administrateur"
                )



            # =====================
            # UPDATE STATUS
            # =====================
            old_status = user.is_active
            user.is_active = is_active


            self.user_repo.update(
                user
            )


            if is_active:
                event_type = EventType.USER_ACTIVATED
                message = "Utilisateur activé"
            else:
                event_type = EventType.USER_DEACTIVATED
                message = "Utilisateur désactivé"


            self.event_service.log(
                type=event_type,
                message=message,
                user_id=current_admin.id,
                event_metadata={
                    "email": user.email
                }
            )
            # =====================
            # COMMIT
            # =====================

            self.uow.commit()

            logger.info(
    "Statut utilisateur modifié",
    extra={
        "user_id": user.id,
        "old_status": old_status,
        "new_status": user.is_active,
        "admin_id": current_admin.id,
    }
)

            return ToggleUserActiveResponse(

                id=user.id,

                is_active=user.is_active,

                message=(
                    "Statut utilisateur mis à jour"
                )
            )



        except Exception:

            self.uow.rollback()

            logger.exception(
    "Erreur activation compte",
    extra={
        "user_id": user_id
    }
)
            raise