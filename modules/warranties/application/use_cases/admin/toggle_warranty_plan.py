from modules.warranties.domain.exceptions import WarrantyPlanNotFound

from modules.warranties.api.schemas import UpdateWarrantyPlanResponse


class ToggleWarrantyPlanUseCase:


    def __init__(
        self,
        repository,
        unit_of_work,
    ):

        self.repository = repository
        self.unit_of_work = unit_of_work



    def execute(
        self,
        plan_id: str,
        active: bool,
    ):


        # =========================
        # GET PLAN
        # =========================

        plan = (
            self.repository
            .get_by_id(plan_id)
        )


        if not plan:
            raise WarrantyPlanNotFound()


        # =========================
        # TOGGLE STATUS
        # =========================

        plan.active = active


        # =========================
        # UPDATE
        # =========================

        self.repository.update(plan)

        self.unit_of_work.commit()


        # =========================
        # RESPONSE
        # =========================

        return UpdateWarrantyPlanResponse(

            id=plan.id,

            message=(
                "Plan activé avec succès"
                if active
                else
                "Plan désactivé avec succès"
            )

        )