from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.inspections.domain.entities.inspection import Inspection
from modules.inspections.api.schemas import StartInspectionResponse
import uuid


class StartInspectionUseCase:


    def __init__(
        self,
        vehicle_repository,
        inspection_repository,
        job_queue,
        unit_of_work,
    ):

        self.vehicle_repository = vehicle_repository
        self.inspection_repository = inspection_repository
        self.job_queue = job_queue
        self.unit_of_work = unit_of_work



    def execute(
        self,
        vehicle_id: str,
        admin_id: str,
    ):

        try:

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
            # BUSINESS RULE
            # =========================

            vehicle.ensure_can_be_inspected()



            # =========================
            # CREATE INSPECTION
            # =========================

            inspection = Inspection.create(
                id=str(uuid.uuid4()),
                vehicle_id=vehicle.id,
            )


            self.inspection_repository.save(
                inspection
            )



            # =========================
            # CHANGE VEHICLE STATE
            # =========================

            vehicle.request_inspection()


            self.vehicle_repository.update(
                vehicle
            )



            self.unit_of_work.commit()



            # =========================
            # QUEUE JOB
            # =========================

            self.job_queue.enqueue_inspection(
                vehicle.id,
                admin_id,
            )



            return StartInspectionResponse(
                inspection_id=inspection.id,
                vehicle_id=vehicle.id,
                status="QUEUED",
                message="Inspection mise en file d'attente"
            )


        except Exception:

            self.unit_of_work.rollback()

            raise