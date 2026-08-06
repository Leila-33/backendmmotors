from modules.warranties.domain.exceptions import WarrantyPlanNotFound

from modules.warranties.api.schemas import UpdateWarrantyPlanResponse
from modules.applications.domain.enums import EventType


class ToggleWarrantyPlanUseCase:


    def __init__(
        self,
        repository,
        event_service,
        unit_of_work,
    ):
        self.repository = repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work



    def execute(
        self,
        plan_id: str,
        active: bool,
        current_admin
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

        old_status = plan.active

        plan.active = active

        self.repository.update(plan)


        self.event_service.log(
            type=(
                EventType.WARRANTY_PLAN_ACTIVATED
                if active
                else
                EventType.WARRANTY_PLAN_DEACTIVATED
            ),
            message=(
                "Plan de garantie activé"
                if active
                else
                "Plan de garantie désactivé"
            ),
            user_id=current_admin.id,
            event_metadata={
                "plan_id": plan.id,
                "name": plan.name,
                "old_status": old_status,
                "new_status": active,
            }
        )


        self.unit_of_work.commit()


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