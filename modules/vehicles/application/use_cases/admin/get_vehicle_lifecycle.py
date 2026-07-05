from modules.vehicles.api.schemas import (
    VehicleLifecycleDTO
)
from modules.inspections.api.schemas import (
    InspectionDTO
)
from modules.reconditionings.api.schemas import (
    ReconditioningDTO
)


class GetVehicleLifecycleUseCase:

    def __init__(
        self,
        inspection_repository,
        reconditioning_repository
    ):
        self.inspection_repository = inspection_repository
        self.reconditioning_repository = reconditioning_repository

    def execute(
        self,
        vehicle_id: str
    ) -> VehicleLifecycleDTO:

        inspection = (
            self.inspection_repository
            .get_by_vehicle_id(vehicle_id)
        )

        reconditioning = (
            self.reconditioning_repository
            .get_by_vehicle_id(vehicle_id)
        )

        return VehicleLifecycleDTO(
            inspection=(
                InspectionDTO(
                    id=inspection.id,
                    vehicle_id=inspection.vehicle_id,
                    status=inspection.status,
                    engine_score=inspection.engine_score,
                    brakes_score=inspection.brakes_score,
                    tires_score=inspection.tires_score,
                    electronics_score=inspection.electronics_score,
                    safety_score=inspection.safety_score,
                    overall_score=inspection.overall_score,
                    failures=inspection.failures or [],
                    recommended_repairs=inspection.recommended_repairs or [],
                    created_at=inspection.created_at,
                    completed_at=inspection.completed_at,
                )
                if inspection
                else None
            ),
            reconditioning=(
                ReconditioningDTO(
                    id=reconditioning.id,
                    vehicle_id=reconditioning.vehicle_id,
                    status=reconditioning.status,
                    cost=reconditioning.cost,
                    duration_days=reconditioning.duration_days,
                    tasks=reconditioning.tasks or [],
                    started_at=reconditioning.started_at,
                    completed_at=reconditioning.completed_at,
                )
                if reconditioning
                else None
            )
        )