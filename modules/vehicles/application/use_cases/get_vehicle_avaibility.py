from modules.reservations.domain.repositories.reservation_repository import ReservationRepository

class GetVehicleAvailabilityUseCase:

    def __init__(
        self,
        reservation_repository: ReservationRepository
    ):
        self.reservation_repository = (
            reservation_repository
        )

    def execute(
        self,
        vehicle_id: str
    ):

        reservations = (
            self.reservation_repository
            .get_active_by_vehicle_id(vehicle_id)
        )

        return [
            {
                "start": reservation.start_date,
                "end": reservation.end_date
            }
            for reservation in reservations
        ]