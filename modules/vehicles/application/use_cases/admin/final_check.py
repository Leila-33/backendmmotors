from datetime import datetime, timezone

from modules.core.exceptions import VehicleNotFound, ReconditioningNotFound, ReconditioningNotCompleted
from modules.core.enums import ReconditioningStatus, VehicleStatus

class FinalCheckUseCase:

    def __init__(
        self,
        vehicle_repository,
        reconditioning_repository,
    ):
        self.vehicle_repository = vehicle_repository
        self.reconditioning_repository = reconditioning_repository

    def execute(self, vehicle_id: str):

        # =========================
        # LOAD DATA
        # =========================
        vehicle = self.vehicle_repository.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()

        reconditioning = self.reconditioning_repository.get_by_vehicle_id(vehicle_id)

        if not reconditioning:
            raise ReconditioningNotFound()
        # =========================
        # BUSINESS RULES
        # =========================
        if reconditioning.status != ReconditioningStatus.COMPLETED:
            raise ReconditioningNotCompleted()


        # =========================
        # FINAL APPROVAL
        # =========================
        reconditioning.status = ReconditioningStatus.APPROVED

        vehicle.status = VehicleStatus.READY
        vehicle.final_check_at = datetime.now(timezone.utc)
        # =========================
        # SAVE
        # =========================
        self.reconditioning_repository.update(reconditioning)
        self.vehicle_repository.update(vehicle)

        # =========================
        # RETURN RESULT
        # =========================
        return {
            "vehicle_id": vehicle.id,
            "vehicle_status": vehicle.status,
            "reconditioning_status": reconditioning.status,
            "final_check_at": vehicle.final_check_at,
        }