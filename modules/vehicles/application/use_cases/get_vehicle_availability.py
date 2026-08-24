from modules.reservations.domain.repositories.reservation_repository import (
    ReservationRepository,
)
from modules.vehicles.domain.repositories.vehicle_repository import (
    VehicleRepository,
)
from modules.vehicles.domain.exceptions import VehicleNotFound


class GetVehicleAvailabilityUseCase:

    def __init__(
        self,
        reservation_repository: ReservationRepository,
        vehicle_repository: VehicleRepository,
    ):
        self.reservation_repository = reservation_repository
        self.vehicle_repository = vehicle_repository

    def execute(
        self,
        vehicle_id: str,
    ) -> list[dict]:

        # =========================
        # VEHICLE CHECK
        # =========================

        vehicle = (
            self.vehicle_repository
            .get_by_id(vehicle_id)
        )

        if vehicle is None:
            raise VehicleNotFound()

        # =========================
        # RESERVATIONS
        # =========================

        reservations = (
            self.reservation_repository
            .get_active_by_vehicle_id(vehicle_id)
        )

        # =========================
        # AVAILABILITY
        # =========================

        return [
            {
                "start": reservation.start_date,
                "end": reservation.end_date,
            }
            for reservation in reservations
        ]