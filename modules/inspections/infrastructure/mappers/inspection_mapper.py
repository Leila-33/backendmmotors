from modules.inspections.domain.entities.inspection import Inspection
from modules.inspections.infrastructure.db.inspection_model import InspectionModel
from modules.inspections.domain.enums import InspectionStatus
from modules.inspections.api.schemas import InspectionResponse
from modules.inspections.application.results.inspection_result import InspectionResult

from modules.inspections.api.schemas import StartInspectionResponse
from modules.inspections.application.results.start_inspection_result import (
    StartInspectionResult,
)

class InspectionMapper:


    @staticmethod
    def to_model(
        inspection: Inspection
    ) -> InspectionModel:


        return InspectionModel(

            id=inspection.id,

            vehicle_id=inspection.vehicle_id,

            status=inspection.status.value,


            engine_score=inspection.engine_score,

            brakes_score=inspection.brakes_score,

            tires_score=inspection.tires_score,

            electronics_score=inspection.electronics_score,

            safety_score=inspection.safety_score,


            overall_score=inspection.overall_score,


            failures=inspection.failures,

            recommended_repairs=
                inspection.recommended_repairs,


            started_at=inspection.started_at,

            completed_at=inspection.completed_at,

            created_at=inspection.created_at,

        )



    @staticmethod
    def to_domain(
        model: InspectionModel
    ) -> Inspection:


        return Inspection(

            id=model.id,

            vehicle_id=model.vehicle_id,


            status=InspectionStatus(
                model.status
            ),


            engine_score=model.engine_score,

            brakes_score=model.brakes_score,

            tires_score=model.tires_score,

            electronics_score=model.electronics_score,

            safety_score=model.safety_score,


            overall_score=model.overall_score,


            failures=model.failures or [],

            recommended_repairs=
                model.recommended_repairs or [],


            started_at=model.started_at,

            completed_at=model.completed_at,

            created_at=model.created_at,
        )



    @staticmethod
    def update_model(
        model: InspectionModel,
        inspection: Inspection
    ) -> None:


        model.status = (
            inspection.status.value
        )

        model.engine_score = (
            inspection.engine_score
        )

        model.brakes_score = (
            inspection.brakes_score
        )

        model.tires_score = (
            inspection.tires_score
        )

        model.electronics_score = (
            inspection.electronics_score
        )

        model.safety_score = (
            inspection.safety_score
        )

        model.overall_score = (
            inspection.overall_score
        )

        model.failures = (
            inspection.failures
        )

        model.recommended_repairs = (
            inspection.recommended_repairs
        )

        model.started_at = (
            inspection.started_at
        )

        model.completed_at = (
            inspection.completed_at
        )

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