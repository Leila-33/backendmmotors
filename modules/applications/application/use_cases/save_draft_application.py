from modules.applications.domain.enums import EventType
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.application.services.event_service import EventService
from modules.auth.domain.entities.user import User
from core.database.unit_of_work import UnitOfWork
import logging

logger = logging.getLogger(__name__)


class SaveDraftApplicationUseCase:

    def __init__(
        self,
        application_form_service,
        event_service: EventService,
        uow: UnitOfWork,
    ):
        self.application_form_service = application_form_service
        self.event_service = event_service
        self.uow = uow


    def execute(
        self,
        dto,
        current_user: User
    ):

        try:

            result = self.application_form_service.save(
                dto=dto,
                current_user=current_user,
            )


            if result.is_new:

                 self.event_service.log(
                        application_id=result.application.id,
                        user_id=current_user.id,
                        type=EventType.APPLICATION_CREATED,
                        message="Dossier créé.",
                    )
                


            self.uow.commit()

            logger.info(
    "Brouillon application sauvegardé",
    extra={
        "application_id": result.application.id,
        "user_id": current_user.id,
        "status": result.application.status.value,
    }
)
            return result.application

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur sauvegarde brouillon application",
                extra={
                    "user_id": current_user.id,
                    "application_id": result.application.id,
                }
            )

            raise