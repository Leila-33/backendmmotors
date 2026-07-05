from modules.core.exceptions import VehicleNotFound, VehicleNotEligibleForInspection, InspectionAlreadyCompleted, InspectionAlreadyRunning

from modules.core.enums import VehicleStatus
from uuid import uuid4
from modules.inspections.domain.entities.inspection import Inspection
from modules.core.enums import InspectionStatus

class StartInspectionUseCase:

    def __init__(self, vehicle_repository, inspection_repository, job_queue):
        self.vehicle_repository = vehicle_repository
        self.inspection_repository = inspection_repository
        self.job_queue = job_queue

    def execute(self, vehicle_id: str, admin_id):

        vehicle = self.vehicle_repository.get_by_id(vehicle_id)

        if vehicle is None:
            raise VehicleNotFound()

        # =========================
        # SAFE STATE MACHINE
        # =========================

        if vehicle.status == VehicleStatus.INSPECTION_PENDING:
            raise InspectionAlreadyRunning()

        if vehicle.status == VehicleStatus.INSPECTED:
            raise InspectionAlreadyCompleted()

        if vehicle.status != VehicleStatus.AVAILABLE:
            raise VehicleNotEligibleForInspection()

        # =========================
        # UPDATE STATUS
        # =========================
      
        inspection = Inspection.create(
    id=str(uuid4()),
    vehicle_id=vehicle_id,
)

        self.inspection_repository.save(inspection)
        vehicle.status = VehicleStatus.INSPECTION_PENDING
        self.vehicle_repository.update(vehicle)
        # =========================
        # QUEUE JOB
        # =========================
        self.job_queue.enqueue_inspection(inspection.id, admin_id)

        return {
            "status": "QUEUED",
            "vehicle_id": vehicle_id,
        }