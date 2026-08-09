from uuid import uuid4
from modules.applications.domain.entities.event import Event
from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.applications.domain.entities.application import Application
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from core.database.unit_of_work import UnitOfWork
from modules.applications.application.services.event_service import EventService
from modules.auth.domain.entities.user import User
from modules.applications.domain.exceptions import ApplicationNotArchived
import logging

logger = logging.getLogger(__name__)

class UnarchiveApplicationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        event_service: EventService,
        unit_of_work: UnitOfWork,
    ):
        self.application_repository = application_repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work


    # =========================
    # EXECUTE
    # =========================
    def execute(
        self,
        application_id: str,
        current_admin: User,
    ) -> Application:

        try:
            # =========================
            # GET APPLICATION
            # =========================
            application = (
                self.application_repository.get_by_id(
                    application_id
                )
            )

            if not application:
                raise ApplicationNotFound()


            # =========================
            # VALIDATION
            # =========================
            if not application.is_archived:
                raise ApplicationNotArchived()


            # =========================
            # UNARCHIVE
            # =========================
            application.is_archived = False

            self.application_repository.update(
                application
            )


            # =========================
            # EVENT
            # =========================
            self.event_service.log(

                    application_id=application.id,

                    user_id=current_admin.id,

                    type=EventType.APPLICATION_UNARCHIVED,

                    message=(
                        "Dossier restauré depuis les archives."
                    ),

                    event_metadata={
                        "restored_by": current_admin.id,
                        "vehicle_id": application.vehicle_id,
                        "status": (
                            application.status.value
                            if application.status
                            else None
                        ),
                    },
                )
            


            # =========================
            # COMMIT
            # =========================
            self.unit_of_work.commit()

            logger.info(
    "Application désarchivée",
    extra={
        "application_id": application.id,
        "admin_id": current_admin.id,
    }
)

            return application

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
    "Erreur désarchivage application",
    extra={
        "application_id": application_id
    }
)
            raise