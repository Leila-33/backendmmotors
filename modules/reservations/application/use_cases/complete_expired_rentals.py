import logging
from datetime import datetime, timezone

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)

from modules.reservations.domain.enums import (
    ReservationStatus,
)

from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository,
)

from modules.reservations.domain.repositories.reservation_repository import (
    ReservationRepository,
)

from core.database.unit_of_work import UnitOfWork

from modules.applications.application.services.event_service import (
    EventService,
)


logger = logging.getLogger(__name__)


class CompleteExpiredRentalsUseCase:
    """
    Termine automatiquement les réservations de location arrivées
    à leur échéance et met à jour les dossiers associés.

    Chaque location clôturée est enregistrée dans l'historique
    des événements avec une origine système.
    """
    def __init__(
        self,
        reservation_repository: ReservationRepository,
        application_repository: ApplicationRepository,
        event_service: EventService,
        unit_of_work: UnitOfWork,
    ):
        self.reservation_repository = (
            reservation_repository
        )

        self.application_repository = (
            application_repository
        )

        self.event_service = event_service

        self.unit_of_work = unit_of_work

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(self) -> int:

        try:

            now = datetime.now(
                timezone.utc
            )

            reservations = (
                self.reservation_repository
                .find_expired_active(now)
            )

            completed_count = 0

            for reservation in reservations:

                # =================================================
                # RESERVATION
                # =================================================

                reservation.status = (
                    ReservationStatus.COMPLETED
                )

                self.reservation_repository.update(
                    reservation
                )

                # =================================================
                # APPLICATION
                # =================================================

                application = (
                    self.application_repository
                    .get_by_id(
                        reservation.application_id
                    )
                )

                if application is None:

                    logger.warning(
                        "Application introuvable pour une réservation expirée",
                        extra={
                            "reservation_id": reservation.id,
                            "application_id": (
                                reservation.application_id
                            ),
                        },
                    )

                    continue

                if (
                    application.status
                    != ApplicationStatus.COMPLETED
                ):

                    application.status = (
                        ApplicationStatus.COMPLETED
                    )

                    self.application_repository.update(
                        application
                    )

                # =================================================
                # EVENT
                # =================================================

                self.event_service.log(

                    application_id=application.id,

                    user_id=application.user_id,

                    vehicle_id=reservation.vehicle_id,

                    type=EventType.RENTAL_COMPLETED,

                    message=(
                        "Location terminée automatiquement."
                    ),

                    event_metadata={
                        "reservation_id": reservation.id,
                        "completed_by": "SYSTEM",
                    },
                )

                completed_count += 1

            # =====================================================
            # COMMIT
            # =====================================================

            self.unit_of_work.commit()

            # =====================================================
            # SUCCESS LOG
            # =====================================================

            logger.info(
                "Locations expirées complétées",
                extra={
                    "count": completed_count,
                },
            )

            return completed_count

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors de la clôture automatique des locations",
            )

            raise
