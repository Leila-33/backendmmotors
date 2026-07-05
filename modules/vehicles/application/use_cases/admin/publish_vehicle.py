from datetime import datetime, timezone

from modules.core.exceptions import VehicleNotFound, VehicleAlreadyPublished, VehicleNotReadyForPublication
from modules.core.enums import VehicleStatus
class PublishVehicleUseCase:

    def __init__(self, vehicle_repository):
        self.vehicle_repository = vehicle_repository

    def execute(self, vehicle_id: int):

        vehicle = self.vehicle_repository.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()

        # =========================
        # BUSINESS RULES
        # =========================
        if vehicle.status == VehicleStatus.PUBLISHED:
            raise VehicleAlreadyPublished()

        if vehicle.status != VehicleStatus.READY:
            raise VehicleNotReadyForPublication()

        # =========================
        # PUBLISH
        # =========================
        vehicle.status = VehicleStatus.PUBLISHED
        vehicle.is_available = True
        vehicle.published_at = datetime.now(timezone.utc)

        self.vehicle_repository.update(vehicle)

        # =========================
        # RETURN FULL VEHICLE (IMPORTANT)
        # =========================
        return vehicle