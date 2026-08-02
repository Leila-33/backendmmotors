from modules.applications.domain.exceptions import ApplicationNotFound
from modules.applications.domain.enums import EventType
from modules.reservations.domain.enums import ReservationStatus
from uuid import uuid4
from modules.applications.domain.entities.event import Event
from modules.applications.domain.policies.restore_application_policy import RestoreApplicationPolicy
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from modules.applications.domain.repositories.event_repository import EventRepository
from modules.applications.application.services.restore_application_service import RestoreApplicationService
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.entities.application import Application


class RestoreCancelledApplicationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        reservation_repository: ReservationRepository,
        event_repository: EventRepository,
        restore_application_service: RestoreApplicationService,
        unit_of_work: UnitOfWork,
    ):
        self.application_repository = application_repository
        self.reservation_repository = reservation_repository
        self.event_repository = event_repository
        self.restore_application_service = (
            restore_application_service
        )
        self.unit_of_work = unit_of_work


    # =========================
    # EXECUTE
    # =========================
    def execute(
        self,
        application_id: str,
    ) -> Application:


        # =========================
        # LOAD APPLICATION
        # =========================
        application = (
            self.application_repository.get_by_id(
                application_id
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
        self.event_repository.save(
            Event(
                id=str(uuid4()),

                application_id=application.id,

                user_id=application.user_id,

                type=EventType.APPLICATION_RESTORED,

                message=(
                    "Dossier restauré par administrateur."
                ),

                event_metadata={
                    "action": "restore",
                },
            )
        )


        # =========================
        # COMMIT
        # =========================
        self.unit_of_work.commit()


        return application