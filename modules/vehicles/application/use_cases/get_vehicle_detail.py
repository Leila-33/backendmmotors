from modules.vehicles.application.use_cases.admin.create_vehicle import VehicleMapper
from modules.core.exceptions import (
    VehicleNotFound
)
class GetVehicleDetail:

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
        return VehicleMapper.to_response(vehicle)