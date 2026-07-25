from datetime import datetime, timezone

from modules.vehicles.domain.exceptions import VehicleNotFound, VehicleAlreadyPublished, VehicleNotReadyForPublication
from modules.vehicles.domain.enums import VehicleStatus

from datetime import datetime, timezone

class PublishVehicleUseCase:

    def __init__(
        self,
        vehicle_repository,
        unit_of_work,
    ):
        self.vehicle_repository = vehicle_repository
        self.unit_of_work = unit_of_work

    def execute(
        self,
        vehicle_id: str,
    ):

        vehicle = self.vehicle_repository.get_by_id(
            vehicle_id
        )

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
        # DOMAIN
        # =========================
        vehicle.publish()

        # =========================
        # SAVE
        # =========================
        self.vehicle_repository.update(
            vehicle
        )

        self.unit_of_work.commit()

        return vehicle