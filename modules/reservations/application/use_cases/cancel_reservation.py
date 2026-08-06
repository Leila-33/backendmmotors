from datetime import datetime, timezone
from modules.applications.domain.enums import EventType
from modules.reservations.domain.enums import ReservationStatus
from modules.reservations.domain.exceptions import (
    ReservationNotFound,
    ReservationAlreadyCancelled,
    ReservationAlreadyStarted,
    CannotCancelReservation
) 
from modules.auth.domain.enums import UserRole
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from core.database.unit_of_work import UnitOfWork
from modules.reservations.domain.entities.reservation import Reservation
from modules.applications.application.services.event_service import EventService

class CancelReservationUseCase:

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        event_service: EventService,
        unit_of_work: UnitOfWork,
    ):
        self.reservation_repository = reservation_repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        reservation_id: str,
        role: str,
        user_id: str,
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

            # =========================
            # VALIDATION
            # =========================
            if reservation.status == ReservationStatus.CANCELLED:
                raise ReservationAlreadyCancelled()

            if reservation.status in (
                ReservationStatus.COMPLETED,
                ReservationStatus.CANCELLED,
            ):
                raise CannotCancelReservation()

            if (
            role != UserRole.ADMIN
            and reservation.status not in (
                ReservationStatus.DRAFT,
                ReservationStatus.ACTIVE,
            )
        ):
                raise CannotCancelReservation()

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
                        "role": role,
                    },
                )

            # =========================
            # COMMIT
            # =========================
            self.unit_of_work.commit()

            return reservation

        except Exception:
            self.unit_of_work.rollback()
            raise