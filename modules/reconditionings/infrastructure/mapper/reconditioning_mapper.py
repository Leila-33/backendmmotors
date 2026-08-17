from modules.reconditionings.domain.entities.reconditioning import Reconditioning
from modules.reconditionings.infrastructure.db.reconditioning_model import ReconditioningModel
from modules.reconditionings.api.schemas import ReconditioningResponse
from modules.reconditionings.application.results.admin.start_reconditioning_result import (
    StartReconditioningResult,
)
from modules.reconditionings.api.schemas import (
    StartReconditioningResponse,
)
class ReconditioningMapper:


    # =========================
    # MODEL -> DOMAIN
    # =========================

    @staticmethod
    def to_domain(
        model: ReconditioningModel
    ) -> Reconditioning:

        return Reconditioning(

            id=model.id,

            vehicle_id=model.vehicle_id,

            status=model.status,

            cost=model.cost,

            duration_days=model.duration_days,

            tasks=(
                model.tasks
                if model.tasks
                else []
            ),

            started_at=model.started_at,

            completed_at=model.completed_at,
        )



    # =========================
    # DOMAIN -> MODEL
    # =========================

    @staticmethod
    def to_model(
        reconditioning: Reconditioning
    ) -> ReconditioningModel:

        return ReconditioningModel(

            id=reconditioning.id,

            vehicle_id=reconditioning.vehicle_id,

            status=reconditioning.status,

            cost=reconditioning.cost,

            duration_days=reconditioning.duration_days,

            tasks=reconditioning.tasks,

            started_at=reconditioning.started_at,

            completed_at=reconditioning.completed_at,
        )



    # =========================
    # UPDATE EXISTING MODEL
    # =========================

    @staticmethod
    def update_model(
        model: ReconditioningModel,
        reconditioning: Reconditioning,
    ) -> ReconditioningModel:


        model.status = (
            reconditioning.status
        )

        model.cost = (
            reconditioning.cost
        )

        model.duration_days = (
            reconditioning.duration_days
        )

        model.tasks = (
            reconditioning.tasks
        )

        model.started_at = (
            reconditioning.started_at
        )

        model.completed_at = (
            reconditioning.completed_at
        )


        return model
    
    
    @staticmethod
    def to_response(
        reconditioning: Reconditioning
    ) -> ReconditioningResponse:


        return ReconditioningResponse(

            id=reconditioning.id,

            vehicle_id=(
                reconditioning.vehicle_id
            ),

            status=(
                reconditioning.status.value
            ),

            cost=(
                reconditioning.cost
            ),

            duration_days=(
                reconditioning.duration_days
            ),

            tasks=(
                reconditioning.tasks
                or []
            ),

            started_at=(
                reconditioning.started_at
            ),

            completed_at=(
                reconditioning.completed_at
            )
        )


    @staticmethod
    def to_start_response(
        result: StartReconditioningResult,
    ) -> StartReconditioningResponse:

        return StartReconditioningResponse(
            reconditioning_id=result.reconditioning_id,
            vehicle_id=result.vehicle_id,
            status=result.status,
            message=result.message,
        )