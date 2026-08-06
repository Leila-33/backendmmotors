from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.entities.application import Application
from modules.auth.domain.entities.user import User
from modules.applications.domain.policies.archive_application_policy import ArchiveApplicationPolicy
from modules.applications.application.services.event_service import EventService

class ArchiveApplicationUseCase:

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
        ArchiveApplicationPolicy.validate(
            application
        )




        # =========================
        # ARCHIVE
        # =========================
        application.is_archived = True


        self.application_repository.update(
            application
        )


        # =========================
        # EVENT AUDIT
        # =========================
        self.event_service.log(

                application_id=application.id,

                user_id=current_admin.id,

                type=EventType.APPLICATION_ARCHIVED,

                message=(
                    "Dossier archivé par administrateur."
                ),

                event_metadata={
                    "archived_by": current_admin.id,
                    "vehicle_id": application.vehicle_id,
                    "status_before": (
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


        return application