from modules.applications.domain.policies.soft_delete_application_policy import SoftDeleteApplicationPolicy
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.application.services.event_service import EventService
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.entities.application import Application
from datetime import datetime, timezone
from modules.auth.domain.entities.user import User
from modules.applications.domain.enums import EventType

class SoftDeleteApplicationUseCase:

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
        SoftDeleteApplicationPolicy.validate(
            application
        )


        # =========================
        # SOFT DELETE
        # =========================
        application.deleted_at = datetime.now(
            timezone.utc
        )

        self.application_repository.update(
            application
        )


        # =========================
        # EVENT
        # =========================
        self.event_service.log(

                application_id=application.id,

                user_id=current_admin.id,

                type=EventType.APPLICATION_DELETED,

                message=(
                    "Dossier supprimé par administrateur."
                ),

                event_metadata={
                    "deleted_by": current_admin.id,
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


        return application