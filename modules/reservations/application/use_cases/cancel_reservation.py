import logging
from datetime import datetime, timezone

from core.database.unit_of_work import UnitOfWork

from modules.applications.application.services.event_service import EventService
from modules.applications.domain.enums import EventType

from modules.auth.domain.enums import UserRole

from modules.reservations.domain.entities.reservation import Reservation
from modules.reservations.domain.enums import ReservationStatus
from modules.reservations.domain.exceptions import (
    CannotCancelReservation,
    ReservationAlreadyCancelled,
    ReservationAlreadyStarted,
    ReservationNotFound,
)
from modules.reservations.domain.repositories.reservation_repository import (
    ReservationRepository,
)
from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound
)
logger = logging.getLogger(__name__)


class CancelReservationUseCase:
    """
    Annule une réservation après vérification des droits de l'utilisateur,
    de l'état de la réservation et de sa date de début.

    L'annulation est enregistrée dans l'historique des événements
    avant la validation de la transaction.
    """
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

    def execute(
        self,
        reservation_id: str,
        user_id: str,
        role: UserRole,
    ) -> Reservation:

        try:
            # =========================
            # LOAD
            # =========================

            reservation = self.reservation_repository.get_by_id(
                reservation_id
            )

            if reservation is None:
                raise ReservationNotFound()



            application = self.application_repository.get_by_id(
                reservation.application_id
            )

            if application is None:
                raise ApplicationNotFound()


            if (
                role != UserRole.ADMIN
                and application.user_id != user_id
            ):
                raise CannotCancelReservation()

            # =========================
            # VALIDATION
            # =========================

            if reservation.status == ReservationStatus.CANCELLED:
                raise ReservationAlreadyCancelled()

            if reservation.status == ReservationStatus.COMPLETED:
                raise CannotCancelReservation()

            if (
                role != UserRole.ADMIN
                and reservation.status
                not in (
                    ReservationStatus.DRAFT,
                    ReservationStatus.PENDING,
                    ReservationStatus.ACTIVE,
                )
            ):
                raise CannotCancelReservation()

            # =========================
            # DATE VALIDATION
            # =========================

            now = datetime.now(timezone.utc)

            if reservation.start_date <= now.date():
                raise ReservationAlreadyStarted()

            # =========================
            # CANCEL
            # =========================

            reservation.status = ReservationStatus.CANCELLED
            reservation.updated_at = now

            self.reservation_repository.update(
                reservation
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                application_id=reservation.application_id,
                user_id=user_id,
                vehicle_id=reservation.vehicle_id,
                type=EventType.RENTAL_CANCELLED,
                message="Réservation annulée avec succès.",
                event_metadata={
                    "reservation_id": reservation.id,
                    "vehicle_id": reservation.vehicle_id,
                    "role": role.value,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            logger.info(
                "Réservation annulée",
                extra={
                    "reservation_id": reservation.id,
                    "actor_id": user_id,
                },
            )

            return reservation

        except Exception:
            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors de l'annulation de la réservation",
                extra={
                    "reservation_id": reservation_id,
                    "actor_id": user_id,
                },
            )

            raise