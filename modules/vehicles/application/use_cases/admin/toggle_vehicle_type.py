from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.core.enums import VehicleType
from modules.core.exceptions import (
    VehicleNotFound,
    InvalidVehicleType,
)
from modules.vehicles.application.use_cases.admin.create_vehicle import VehicleMapper

class ToggleVehicleType:

    def __init__(self, repo: VehicleRepository):
        self.repo = repo

    def execute(self, vehicle_id: str):

        # =========================
        # 1. GET VEHICLE
        # =========================
        vehicle = self.repo.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()

        # =========================
        # 2. TOGGLE TYPE
        # =========================
        mapping = {
            VehicleType.ACHAT: VehicleType.LOCATION,
            VehicleType.LOCATION: VehicleType.ACHAT
        }

        if vehicle.type not in mapping:
            raise InvalidVehicleType()

        vehicle.type = mapping[vehicle.type]

        # =========================
        # 3. SAVE
        # =========================
        self.repo.update(vehicle)

        # =========================
        # 4. RESPONSE
        # =========================
        return VehicleMapper.to_response(vehicle)