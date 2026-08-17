import logging
from uuid import uuid4


from modules.inspections.domain.enums import (
    InspectionStatus,
)
from modules.inspections.domain.exceptions import (
    InspectionNotCompleted,
    InspectionNotFound,
)

from modules.reconditionings.domain.entities.reconditioning import (
    Reconditioning,
)
from modules.reconditionings.domain.enums import (
    ReconditioningStatus,
)
from modules.reconditionings.domain.exceptions import (
    ReconditioningAlreadyRunning,
)

from modules.reconditionings.application.dtos.admin.start_reconditioning_dto import (
    StartReconditioningDTO,
)
from modules.reconditionings.application.results.admin.start_reconditioning_result import (
    StartReconditioningResult,
)

from modules.vehicles.domain.enums import (
    VehicleStatus,
)
from modules.vehicles.domain.exceptions import (
    VehicleNotEligibleForReconditioning,
    VehicleNotFound,
)


logger = logging.getLogger(__name__)


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
        dto: StartReconditioningDTO
    ):

        try:

            # =========================
            # GET VEHICLE
            # =========================

            vehicle = (
                self.vehicle_repository
                .get_by_id(dto.vehicle_id)
            )

            if vehicle is None:
                raise VehicleNotFound()


            # =========================
            # CHECK VEHICLE STATE
            # =========================

            if (
                vehicle.status
                == VehicleStatus.RECONDITIONING
            ):
                raise ReconditioningAlreadyRunning()


            if (
                vehicle.status
                != VehicleStatus.INSPECTED
            ):
                raise VehicleNotEligibleForReconditioning()


            # =========================
            # CHECK INSPECTION
            # =========================

            inspection = (
                self.inspection_repository
                .get_by_vehicle_id(dto.vehicle_id)
            )

            if inspection is None:
                raise InspectionNotFound()


            if (
                inspection.status
                != InspectionStatus.COMPLETED
            ):
                raise InspectionNotCompleted()


            # =========================
            # CHECK EXISTING RECONDITIONING
            # =========================

            existing = (
                self.reconditioning_repository
                .get_by_vehicle_id(dto.vehicle_id)
            )

            if (
                existing
                and existing.status in (
                    ReconditioningStatus.PENDING,
                    ReconditioningStatus.IN_PROGRESS,
                )
            ):
                raise ReconditioningAlreadyRunning()


            # =========================
            # CREATE
            # =========================

            reconditioning = (
                Reconditioning.create(
                    id=str(uuid4()),
                    vehicle_id=dto.vehicle_id,
                )
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


            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()


            # =========================
            # LOG DATABASE SUCCESS
            # =========================

            logger.info(
                "Reconditionnement créé",
                extra={
                    "reconditioning_id": (
                        reconditioning.id
                    ),
                    "vehicle_id": vehicle.id,
                    "admin_id": dto.admin_id,
                }
            )


            # =========================
            # QUEUE
            # =========================

            try:

                self.job_queue.enqueue_reconditioning(
                    reconditioning.id,
                    dto.admin_id,
                )

            except Exception:

                logger.exception(
                    "Échec mise en file du reconditionnement",
                    extra={
                        "reconditioning_id": (
                            reconditioning.id
                        ),
                        "vehicle_id": vehicle.id,
                        "admin_id": dto.admin_id,
                    }
                )

                raise


            # =========================
            # LOG QUEUE SUCCESS
            # =========================

            logger.info(
                "Reconditionnement mis en file d'attente",
                extra={
                    "reconditioning_id": (
                        reconditioning.id
                    ),
                    "vehicle_id": vehicle.id,
                    "admin_id": dto.admin_id,
                }
            )


            return StartReconditioningResult(
                reconditioning_id=reconditioning.id,
                vehicle_id=vehicle.id,
                status=reconditioning.status.value,
                message="Reconditionnement lancé",
            )


        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur démarrage reconditionnement",
                extra={
                    "vehicle_id": dto.vehicle_id,
                    "admin_id": dto.admin_id,
                }
            )

            raise