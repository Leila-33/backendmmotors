from modules.inspections.application.results.inspection_result import (
    InspectionResult,
)
from modules.inspections.domain.exceptions import InspectionNotFound


class GetInspectionUseCase:

    def __init__(
        self,
        inspection_repository,
    ):
        self.inspection_repository = inspection_repository

    def execute(
        self,
        vehicle_id: str,
    ) -> InspectionResult:

        inspection = (
            self.inspection_repository
            .get_by_vehicle_id(
                vehicle_id
            )
        )

        if not inspection:
            raise InspectionNotFound()

        return InspectionResult(
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
            recommended_repairs=(
                inspection.recommended_repairs or []
            ),

            started_at=inspection.started_at,
            completed_at=inspection.completed_at,
            created_at=inspection.created_at,
        )