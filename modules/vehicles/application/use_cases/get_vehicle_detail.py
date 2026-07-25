from modules.vehicles.domain.exceptions import VehicleNotFound

class GetVehicleDetailUseCase:

    def __init__(self, vehicle_repository):
        self.vehicle_repository = vehicle_repository

    def execute(self, vehicle_id: str):

        # =========================
        # 1. GET VEHICLE
        # =========================
        vehicle = self.vehicle_repository.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()

        # =========================
        # 2. RESPONSE
        # =========================
        return vehicle