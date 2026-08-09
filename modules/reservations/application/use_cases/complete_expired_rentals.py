from datetime import datetime, timezone
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.reservations.domain.enums import ReservationStatus
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from core.database.unit_of_work import UnitOfWork
from modules.applications.application.services.event_service import EventService
import logging

logger = logging.getLogger(__name__)

class CompleteExpiredRentalsUseCase:

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        application_repository: ApplicationRepository,
        event_service: EventService,
        unit_of_work: UnitOfWork,
    ):
        self.reservation_repository = reservation_repository
        self.application_repository = application_repository
        self.event_service = event_service
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
                self.event_service.log(
                                application_id=application.id,
                                user_id=None,
                                vehicle_id=reservation.vehicle_id,
                                type=EventType.RENTAL_COMPLETED,
                                message="Location terminée automatiquement.",
                                event_metadata={
                                    "reservation_id": reservation.id,
                                    "completed_by": "SYSTEM",
                                    "user_id": application.user_id,
                                }
                            )
                    

            self.unit_of_work.commit()

            logger.info(
                "Locations expirées complétées",
                extra={
                    "count": len(reservations)
                }
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors de la clôture automatique des locations"
            )

            raise
