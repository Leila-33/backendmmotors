import logging
from uuid import uuid4

from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.inspections.domain.entities.inspection import Inspection
from modules.inspections.application.results.start_inspection_result import (
    StartInspectionResult,
)


logger = logging.getLogger(__name__)


class StartInspectionUseCase:
    """
    Crée une inspection pour un véhicule après vérification
    de son éligibilité, met à jour son état et place l'inspection
    dans la file d'attente pour son traitement.
    """
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
    ) -> StartInspectionResult:

        # =====================================================
        # DATABASE TRANSACTION
        # =====================================================

        try:

            vehicle = (
                self.vehicle_repository
                .get_by_id(vehicle_id)
            )

            if vehicle is None:
                raise VehicleNotFound()

            vehicle.ensure_can_be_inspected()

            inspection = Inspection.create(
                id=str(uuid4()),
                vehicle_id=vehicle.id,
            )

            self.inspection_repository.save(
                inspection
            )

            vehicle.request_inspection()

            self.vehicle_repository.update(
                vehicle
            )

            self.unit_of_work.commit()

            logger.info(
                "Inspection véhicule créée",
                extra={
                    "inspection_id": inspection.id,
                    "vehicle_id": vehicle.id,
                    "admin_id": admin_id,
                },
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création inspection véhicule",
                extra={
                    "vehicle_id": vehicle_id,
                    "admin_id": admin_id,
                },
            )

            raise

        # =====================================================
        # QUEUE
        # =====================================================

        try:

            self.job_queue.enqueue_inspection(
                vehicle.id,
                admin_id,
            )

        except Exception:

            logger.exception(
                "Échec mise en file de l'inspection",
                extra={
                    "inspection_id": inspection.id,
                    "vehicle_id": vehicle.id,
                    "admin_id": admin_id,
                },
            )

            raise

        # =====================================================
        # RESULT
        # =====================================================

        logger.info(
            "Inspection mise en file d'attente",
            extra={
                "inspection_id": inspection.id,
                "vehicle_id": vehicle.id,
                "admin_id": admin_id,
            },
        )

        return StartInspectionResult(
            inspection_id=inspection.id,
            vehicle_id=vehicle.id,
            status="QUEUED",
            message="Inspection mise en file d'attente",
        )