from modules.core.exceptions import VehicleAvailabilityAlreadySet, VehicleNotFound
class SetAvailabilityUseCase:

    def __init__(self, vehicle_repository):
        self.vehicle_repository = vehicle_repository

    def execute(self, vehicle_id: str, value: bool):

        vehicle = self.vehicle_repository.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()

        # =========================
        # NO-OP CHECK
        # =========================
        if vehicle.is_available == value:
            raise VehicleAvailabilityAlreadySet()

        # =========================
        # UPDATE
        # =========================
        vehicle.is_available = value

        self.vehicle_repository.update(vehicle)

        return vehicle