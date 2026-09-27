import logging

from core.database.unit_of_work import UnitOfWork

from modules.applications.application.services.event_service import (
    EventService,
)

from modules.applications.domain.enums import (
    EventType,
)

from modules.applications.application.dtos.save_draft_application_dto import (
    SaveDraftApplicationDTO,
)
logger = logging.getLogger(__name__)


class SaveDraftApplicationUseCase:
    """
    Enregistre ou met à jour le brouillon d'un dossier pour l'utilisateur
    connecté et crée un événement lors de la création d'un nouveau dossier.
    """
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
        dto: SaveDraftApplicationDTO,
        current_user_id: str,
    ):
        result = None

        try:
            result = self.application_form_service.save(
                dto=dto,
                current_user_id=current_user_id,
            )

            if result.is_new:
                self.event_service.log(
                    application_id=result.application.id,
                    user_id=current_user_id,
                    vehicle_id=result.application.vehicle_id,
                    type=EventType.APPLICATION_CREATED,
                    message="Dossier créé.",
                )

            self.uow.commit()

            logger.info(
                "Brouillon application sauvegardé",
                extra={
                    "application_id": result.application.id,
                    "user_id": current_user_id,
                    "status": result.application.status.value,
                },
            )

            return result.application

        except Exception:
            self.uow.rollback()

            logger.exception(
                "Erreur sauvegarde brouillon application",
                extra={
                    "user_id": current_user_id,
                    "application_id": (
                        result.application.id
                        if result and result.application
                        else None
                    ),
                },
            )

            raise