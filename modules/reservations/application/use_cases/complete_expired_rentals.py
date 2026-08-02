from datetime import datetime, timezone
from uuid import uuid4
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.reservations.domain.enums import ReservationStatus
from modules.applications.domain.entities.event import Event
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from modules.applications.domain.repositories.event_repository import EventRepository
from core.database.unit_of_work import UnitOfWork

class CompleteExpiredRentalsUseCase:

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        application_repository: ApplicationRepository,
        event_repository: EventRepository,
        unit_of_work: UnitOfWork,
    ):
        self.reservation_repository = reservation_repository
        self.application_repository = application_repository
        self.event_repository = event_repository
        self.unit_of_work = unit_of_work

    def execute(self) -> None:

        try:

            now = datetime.now(timezone.utc)

            reservations = self.reservation_repository.find_expired_active(now)

            for reservation in reservations:

                # =========================
                # RESERVATION
                # =========================

                reservation.status = ReservationStatus.COMPLETED

                self.reservation_repository.update(
                    reservation
                )

                # =========================
                # APPLICATION
                # =========================
                application = (
                    self.application_repository.get_by_id(
                        reservation.application_id
                    )
                )

                if (
                    application
                    and application.status != ApplicationStatus.COMPLETED
                ):

                    application.status = (
                        ApplicationStatus.COMPLETED
                    )

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
                            type=EventType.RENTAL_COMPLETED,
                            message="Location terminée automatiquement.",
                            event_metadata={
                                "reservation_id": reservation.id
                            },
                        )
                    )

            self.unit_of_work.commit()

        except Exception:
            self.unit_of_work.rollback()
            raise
