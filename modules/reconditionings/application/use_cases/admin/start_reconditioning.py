from datetime import datetime, timezone
from uuid import uuid4

from modules.reconditionings.domain.entities.reconditioning import Reconditioning
from modules.core.enums import ReconditioningStatus, InspectionStatus
from modules.core.exceptions import VehicleNotFound, InspectionNotFound, InspectionNotCompleted, ReconditioningAlreadyRunning
from modules.core.enums import VehicleStatus

class StartReconditioningUseCase:

    def __init__(self, reconditioning_repository, inspection_repository, job_queue, vehicle_repository):
        self.reconditioning_repository = reconditioning_repository
        self.inspection_repository = inspection_repository
        self.job_queue = job_queue
        self.vehicle_repository = vehicle_repository

    def execute(self, vehicle_id: str, admin_id: str):

        # 1. Vérifier véhicule
        vehicle = self.vehicle_repository.get_by_id(vehicle_id)

        if vehicle is None:
            raise VehicleNotFound()

        # 2. Vérifier qu’une inspection existe et est terminée
        inspection = self.inspection_repository.get_by_vehicle_id(vehicle_id)
        if not inspection:
            raise InspectionNotFound()

        if inspection.status != InspectionStatus.COMPLETED :
            raise InspectionNotCompleted()

        # 3. Vérifier si reconditioning existe déjà
        existing = self.reconditioning_repository.get_by_vehicle_id(vehicle_id)

        if existing and existing.status in [
            ReconditioningStatus.IN_PROGRESS,
            ReconditioningStatus.PENDING
        ]:
            raise ReconditioningAlreadyRunning
        vehicle.status = VehicleStatus.RECONDITIONING
        self.vehicle_repository.update(vehicle)

        reconditioning = Reconditioning(
        id=str(uuid4()),
        vehicle_id=vehicle_id,
        status=ReconditioningStatus.PENDING,

        cost=0.0,
        duration_days=0,

        tasks=[],

        started_at=datetime.now(timezone.utc),
        completed_at=None
    )

        # 5. Persist
        self.reconditioning_repository.save(reconditioning)

        # 6. Queue job
        self.job_queue.enqueue_reconditioning(reconditioning.id, admin_id)

        return {
            "status": "QUEUED",
            "reconditioning_id": reconditioning.id
        }