from datetime import datetime, timezone
from uuid import uuid4
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.reservations.domain.enums import ReservationStatus
from modules.applications.domain.entities.event import Event

class CompleteExpiredRentalsUseCase:

    def __init__(
        self,
        reservation_repository,
        application_repository,
        event_repository
    ):
        self.reservation_repository = reservation_repository
        self.application_repository = application_repository
        self.event_repository = event_repository

    def execute(self):

        now = datetime.now(timezone.utc)

        rentals = self.reservation_repository.find_finished_rentals(now)

        for rental in rentals:

            # =========================
            # RESERVATION
            # =========================
            if rental.status == ReservationStatus.COMPLETED:
                continue

            rental.status = ReservationStatus.COMPLETED

            self.reservation_repository.update(rental)

            # =========================
            # APPLICATION
            # =========================
            application = rental.application

            if application and application.status != ApplicationStatus.COMPLETED:
                application.status = ApplicationStatus.COMPLETED
                self.application_repository.update(application)

                # =========================
                # EVENT APPLICATION
                # =========================
                self.event_repository.save(
                    Event(
                        id=str(uuid4()),
                        application_id=application.id,
                        user_id=application.user_id,
                        type=EventType.RENTAL_COMPLETED,
                        message="Location terminée automatiquement (cron).",
                        event_metadata={
                            "reservation_id": rental.id
                        }
                    )
                )

        # =========================
        # COMMIT
        # =========================
        self.reservation_repository.commit()
