from datetime import datetime, timezone
from modules.reconditionings.domain.exceptions import (
    ReconditioningNotFound,
    ReconditioningNotCompleted
)
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotReadyForFinalCheck
)
from modules.reconditionings.domain.enums import ReconditioningStatus
from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.api.schemas import FinalCheckResponse
from modules.applications.domain.enums import EventType

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
        vehicle_id: str,
        current_admin
    ):


        # =========================
        # LOAD VEHICLE
        # =========================

        vehicle = (
            self.vehicle_repository
            .get_by_id(vehicle_id)
        )


        if not vehicle:
            raise VehicleNotFound()



        # =========================
        # LOAD RECONDITIONING
        # =========================

        reconditioning = (
            self.reconditioning_repository
            .get_by_vehicle_id(vehicle_id)
        )


        if not reconditioning:
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

        self.event_service.log(
    type=EventType.FINAL_CHECK_COMPLETED,
    message="Contrôle final terminé",
    vehicle_id=vehicle.id,
    user_id=current_admin.id,
    event_metadata={
        "final_check_at ": vehicle.final_check_at,
    }
)
        self.unit_of_work.commit()



        # =========================
        # RESPONSE
        # =========================

        return FinalCheckResponse(

            vehicle_id=vehicle.id,

            vehicle_status=(
                vehicle.status.value
            ),

            reconditioning_status=(
                reconditioning.status.value
            ),

            final_check_at=(
                vehicle.final_check_at
            )
        )