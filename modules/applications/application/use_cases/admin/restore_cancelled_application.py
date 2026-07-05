from datetime import date, datetime, timezone
from modules.core.exceptions import ApplicationNotFound
from modules.core.enums import ApplicationStatus, ReservationStatus
from uuid import uuid4
from modules.core.enums import EventType
from modules.applications.domain.entities.event import Event
from modules.applications.domain.policies.restore_application_policy import RestoreApplicationPolicy


class RestoreCancelledApplicationUseCase:

    def __init__(
        self,
        application_repository,
        reservation_repository,
        event_repository
    ):
        self.application_repository = (
            application_repository
        )
        self.reservation_repository = (
            reservation_repository
        )
        self.event_repository = (
            event_repository
        )

    def execute(
        self,
        application_id: str,
        role: str = "admin"
    ):

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
            application,
            self.reservation_repository
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
                    "Dossier restauré par "
                    f"{'administrateur' if role == 'admin' else 'client'}."
                ),
                event_metadata={
                    "role": role
                }
            )
        )

        self.application_repository.commit()

        return application