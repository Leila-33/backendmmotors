from datetime import datetime, timezone
import logging

from modules.reconditionings.domain.exceptions import (
    ReconditioningNotFound,
    ReconditioningNotCompleted,
)

from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotReadyForFinalCheck,
)

from modules.reconditionings.domain.enums import (
    ReconditioningStatus,
)

from modules.vehicles.domain.enums import (
    VehicleStatus,
)

from modules.applications.domain.enums import (
    EventType,
)

from modules.vehicles.application.dtos.admin.vehicle_admin_action_dto import (
    VehicleAdminActionDTO,
)

from modules.vehicles.application.results.admin.final_check_result import (
    FinalCheckResult,
)


logger = logging.getLogger(__name__)


class FinalCheckUseCase:

    def __init__(
        self,
        vehicle_repository,
        reconditioning_repository,
        event_service,
        unit_of_work,
    ):
        self.vehicle_repository = vehicle_repository
        self.reconditioning_repository = (
            reconditioning_repository
        )
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: VehicleAdminActionDTO,
    ) -> FinalCheckResult:

        try:

            # =========================
            # LOAD VEHICLE
            # =========================

            vehicle = (
                self.vehicle_repository
                .get_by_id(dto.vehicle_id)
            )

            if vehicle is None:
                raise VehicleNotFound()

            # =========================
            # LOAD RECONDITIONING
            # =========================

            reconditioning = (
                self.reconditioning_repository
                .get_by_vehicle_id(
                    dto.vehicle_id
                )
            )

            if reconditioning is None:
                raise ReconditioningNotFound()

            # =========================
            # BUSINESS RULES
            # =========================

            if (
                reconditioning.status
                != ReconditioningStatus.COMPLETED
            ):
                raise ReconditioningNotCompleted()

            # =========================
            # CHECK VEHICLE STATE
            # =========================

            if (
                vehicle.status
                != VehicleStatus.RECONDITIONED
            ):
                raise VehicleNotReadyForFinalCheck()

            # =========================
            # DOMAIN TRANSITION
            # =========================

            reconditioning.approve()

            vehicle.mark_as_ready()

            vehicle.final_check_at = (
                datetime.now(timezone.utc)
            )

            # =========================
            # PERSISTENCE
            # =========================

            self.reconditioning_repository.update(
                reconditioning
            )

            self.vehicle_repository.update(
                vehicle
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.FINAL_CHECK_COMPLETED,
                message="Contrôle final terminé",
                vehicle_id=vehicle.id,
                user_id=dto.admin_id,
                event_metadata={
                    "final_check_at": (
                        vehicle.final_check_at.isoformat()
                    ),
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            logger.info(
                "Contrôle final terminé",
                extra={
                    "final_check_at": (
                        vehicle.final_check_at.isoformat()
                    ),
                    "vehicle_id": vehicle.id,
                    "admin_id": dto.admin_id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return FinalCheckResult(
                vehicle_id=vehicle.id,
                vehicle_status=vehicle.status.value,
                reconditioning_status=(
                    reconditioning.status.value
                ),
                final_check_at=(
                    vehicle.final_check_at
                ),
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur contrôle final",
                extra={
                    "vehicle_id": dto.vehicle_id,
                    "admin_id": dto.admin_id,
                },
            )

            raise