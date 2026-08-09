from modules.warranties.domain.exceptions import WarrantyPlanNotFound
from modules.warranties.api.schemas import UpdateWarrantyPlanResponse
from modules.applications.domain.enums import EventType
import logging

logger = logging.getLogger(__name__)

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

        try:

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

            if active:
                plan.activate()
            else:
                plan.deactivate()

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


            # =========================
            # UPDATE
            # =========================

            self.repository.update(plan)

            self.unit_of_work.commit()
            
            logger.info(
    "Statut plan de garantie modifié",
    extra={
        "plan_id": plan.id,
        "old_active": old_status,
        "new_active": active,
    },
)
        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur modification statut plan de garantie",
                extra={
                    "plan_id": plan_id,
                    "active": active,
                },
            )

            raise
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