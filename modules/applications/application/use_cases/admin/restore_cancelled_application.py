import logging

from core.database.unit_of_work import UnitOfWork

from modules.applications.application.services.event_service import (
    EventService,
)
from modules.applications.application.services.restore_application_service import (
    RestoreApplicationService,
)

from modules.applications.domain.entities.application import (
    Application,
)
from modules.applications.domain.enums import (
    EventType,
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)
from modules.applications.domain.policies.restore_application_policy import (
    RestoreApplicationPolicy,
)
from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository,
)
from modules.applications.application.dtos.admin.application_id_dto import ApplicationIdDTO

from modules.auth.domain.entities.user import (
    User,
)

from modules.reservations.domain.enums import (
    ReservationStatus,
)
from modules.reservations.domain.repositories.reservation_repository import (
    ReservationRepository,
)


logger = logging.getLogger(__name__)

class RestoreCancelledApplicationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        reservation_repository: ReservationRepository,
        event_service: EventService,
        restore_application_service: RestoreApplicationService,
        unit_of_work: UnitOfWork,
    ):
        self.application_repository = application_repository
        self.reservation_repository = reservation_repository
        self.event_service = event_service
        self.restore_application_service = (
            restore_application_service
        )
        self.unit_of_work = unit_of_work


    # =========================
    # EXECUTE
    # =========================
    def execute(
        self,
        dto: ApplicationIdDTO,
        current_admin: User,
    ) -> Application:

        try:
            # =========================
            # LOAD APPLICATION
            # =========================
            application = (
                self.application_repository.get_by_id(
                    dto.application_id
                )
            )

            if not application:
                raise ApplicationNotFound()


            # =========================
            # POLICY
            # =========================
            RestoreApplicationPolicy.validate(
                application
            )


            # =========================
            # RENTAL VALIDATION
            # =========================
            self.restore_application_service.validate_rental(
                application
            )


            # =========================
            # RESTORE RESERVATION
            # =========================
            if application.reservation:

                application.reservation.status = (
                    ReservationStatus.ACTIVE
                )

                self.reservation_repository.update(
                    application.reservation
                )


            # =========================
            # RESTORE APPLICATION
            # =========================
            application.status = (
                application.previous_status
            )

            application.previous_status = None


            self.application_repository.update(
                application
            )


            # =========================
            # EVENT
            # =========================
            self.event_service.log(
        application_id=application.id,
        user_id=current_admin.id,
        vehicle_id=application.vehicle_id,
        type=EventType.APPLICATION_RESTORED,
        message="Dossier restauré par administrateur.",
        event_metadata={
            "application_user_id": application.user_id,
            "action": "restore",
        },
    )
            


            # =========================
            # COMMIT
            # =========================
            self.unit_of_work.commit()

            logger.info(
    "Application restaurée",
    extra={
        "application_id": application.id,
        "admin_id": current_admin.id,
    }
)
            return application
        
        except Exception:
        
            self.unit_of_work.rollback()
            
            logger.exception(
    "Erreur restauration application",
    extra={
        "application_id": dto.application_id
    }
)
            raise