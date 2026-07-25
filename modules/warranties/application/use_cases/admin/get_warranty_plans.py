from modules.warranties.infrastructure.mappers.warranty_plan_mapper import (
    WarrantyPlanMapper
)


class GetWarrantyPlansUseCase:


    def __init__(
        self,
        repository,
    ):

        self.repository = repository



    def execute(self):

        # =========================
        # GET ALL
        # =========================

        plans = (
            self.repository
            .find_all()
        )


        # =========================
        # RESPONSE
        # =========================

        return [

            WarrantyPlanMapper.to_response(plan)

            for plan in plans

        ]