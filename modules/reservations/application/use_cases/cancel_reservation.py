from datetime import datetime, timezone
from modules.applications.domain.enums import EventType
from modules.reservations.domain.enums import ReservationStatus
from modules.reservations.domain.exceptions import (
    ReservationNotFound,
    ReservationAlreadyCancelled,
    ReservationAlreadyStarted,
    CannotCancelReservation
) 
from uuid import uuid4
from modules.applications.domain.entities.event import Event
from modules.auth.domain.enums import UserRole

class CancelReservationUseCase:

    def __init__(self, reservation_repository, event_repository):
        self.reservation_repository = reservation_repository
        self.event_repository = event_repository

    def execute(self, reservation_id: str, role: str, user_id):

        reservation = self.reservation_repository.get_by_id(reservation_id)

        if not reservation:
            raise ReservationNotFound()

        if reservation.status == ReservationStatus.CANCELLED:
            raise ReservationAlreadyCancelled()

        # =========================
        # BUSINESS RULE
        # =========================
        if role != UserRole.ADMIN:
            if reservation.status != ReservationStatus.ACTIVE:
                raise CannotCancelReservation()


        # =========================
        # OPTIONAL: DATE RULE
        # =========================
        now = datetime.now(timezone.utc)

        if reservation.start_date <= now.date():
            raise ReservationAlreadyStarted()
        
        reservation.status = ReservationStatus.CANCELLED
        reservation.updated_at = now
        self.reservation_repository.update(reservation)

        self.event_repository.save(
            Event(
                id=str(uuid4()),
                application_id=reservation.application_id,
                user_id=user_id,
                type=EventType.RESERVATION_CANCELLED,
                message="Réservation annulée avec succès.",
                event_metadata={
                    "reservation_id": reservation.id,
                    "vehicle_id": reservation.vehicle_id
                }
            )
        )

        self.reservation_repository.commit()

        return reservation