from modules.reservations.domain.entities.reservation import Reservation
from modules.core.enums import ReservationStatus
from modules.core.exceptions import VehicleNotAvailable, ReservationNotFound, Unauthorized


class CreateReservationUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, data, user_id):

        if self.repo.exists_overlap(
            data.vehicle_id,
            data.start_date,
            data.end_date
        ):
            raise VehicleNotAvailable()

        reservation = Reservation(
            vehicle_id=data.vehicle_id,
            user_id=user_id,
            start_date=data.start_date,
            end_date=data.end_date,
            status=ReservationStatus.ACTIVE
        )

        return self.repo.create(reservation)


class CancelReservationUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, reservation_id, user_id):

        reservation = self.repo.get_by_id(reservation_id)

        if not reservation:
            raise ReservationNotFound()

        if reservation.user_id != user_id:
            raise Unauthorized()

        if reservation.status == ReservationStatus.CANCELLED:
            return reservation

        return self.repo.cancel(reservation_id)