from uuid import uuid4
from modules.reconditionings.domain.entities.reconditioning import Reconditioning
from modules.reconditionings.domain.enums import ReconditioningStatus
from modules.inspections.domain.enums import InspectionStatus
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotEligibleForReconditioning
)
from modules.reconditionings.domain.exceptions import ReconditioningAlreadyRunning
from modules.inspections.domain.exceptions import InspectionNotFound, InspectionNotCompleted
from modules.vehicles.domain.enums import VehicleStatus
from modules.reconditionings.api.schemas import StartReconditioningResponse

class StartReconditioningUseCase:

    def __init__(
        self,
        reconditioning_repository,
        inspection_repository,
        vehicle_repository,
        job_queue,
        unit_of_work,
    ):
        self.reconditioning_repository = (
            reconditioning_repository
        )
        self.inspection_repository = (
            inspection_repository
        )
        self.vehicle_repository = (
            vehicle_repository
        )
        self.job_queue = job_queue
        self.unit_of_work = unit_of_work



    def execute(
        self,
        vehicle_id: str,
        admin_id: str,
    ):


        # =========================
        # GET VEHICLE
        # =========================

        vehicle = (
            self.vehicle_repository
            .get_by_id(vehicle_id)
        )


        if vehicle is None:
            raise VehicleNotFound()



        # =========================
        # CHECK VEHICLE STATE
        # =========================

        if vehicle.status == VehicleStatus.RECONDITIONING:
            raise ReconditioningAlreadyRunning()


        if vehicle.status != VehicleStatus.INSPECTED:
            raise VehicleNotEligibleForReconditioning()



        # =========================
        # CHECK INSPECTION
        # =========================

        inspection = (
            self.inspection_repository
            .get_by_vehicle_id(vehicle_id)
        )


        if inspection is None:
            raise InspectionNotFound()


        if inspection.status != InspectionStatus.COMPLETED:
            raise InspectionNotCompleted()



        # =========================
        # CHECK EXISTING RECONDITIONING
        # =========================

        existing = (
            self.reconditioning_repository
            .get_by_vehicle_id(vehicle_id)
        )


        if existing and existing.status in [
            ReconditioningStatus.PENDING,
            ReconditioningStatus.IN_PROGRESS,
        ]:
            raise ReconditioningAlreadyRunning()



        # =========================
        # CREATE RECONDITIONING
        # =========================

        reconditioning = Reconditioning.create(

            id=str(uuid4()),

            vehicle_id=vehicle_id,

        )



        # =========================
        # DOMAIN TRANSITION
        # =========================

        vehicle.start_reconditioning()



        # =========================
        # SAVE
        # =========================

        self.reconditioning_repository.save(
            reconditioning
        )


        self.vehicle_repository.update(
            vehicle
        )



        self.unit_of_work.commit()



        # =========================
        # QUEUE
        # =========================

        self.job_queue.enqueue_reconditioning(
            reconditioning.id,
            admin_id
        )



        return StartReconditioningResponse(

            reconditioning_id=(
                reconditioning.id
            ),

            vehicle_id=(
                vehicle.id
            ),

            status=(
                reconditioning.status.value
            ),

            message=(
                "Reconditionnement lancé"
            )
        )