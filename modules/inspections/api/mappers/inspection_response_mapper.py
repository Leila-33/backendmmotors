from modules.inspections.api.schemas import (
    InspectionResponse,
    StartInspectionResponse,
)

from modules.inspections.application.results.inspection_result import (
    InspectionResult,
)

from modules.inspections.application.results.start_inspection_result import (
    StartInspectionResult,
)


class InspectionResponseMapper:

    @staticmethod
    def to_response(
        result: InspectionResult,
    ) -> InspectionResponse:

        return InspectionResponse(
            id=result.id,
            vehicle_id=result.vehicle_id,
            status=result.status.value,

            engine_score=result.engine_score,
            brakes_score=result.brakes_score,
            tires_score=result.tires_score,
            electronics_score=result.electronics_score,
            safety_score=result.safety_score,

            overall_score=result.overall_score,

            failures=result.failures,
            recommended_repairs=result.recommended_repairs,

            started_at=result.started_at,
            completed_at=result.completed_at,
            created_at=result.created_at,
        )

    @staticmethod
    def start(
        result: StartInspectionResult,
    ) -> StartInspectionResponse:

        return StartInspectionResponse(
            inspection_id=result.inspection_id,
            vehicle_id=result.vehicle_id,
            status=result.status,
            message=result.message,
        )