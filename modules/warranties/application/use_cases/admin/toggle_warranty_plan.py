import logging

from modules.warranties.domain.exceptions import (
    WarrantyPlanNotFound,
)
from modules.applications.domain.enums import EventType
from modules.warranties.application.dtos.admin.toggle_warranty_plan_dto import (
    ToggleWarrantyPlanDTO,
)

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
        dto: ToggleWarrantyPlanDTO,
    ):

        try:

            # =========================
            # GET PLAN
            # =========================

            plan = self.repository.get_by_id(
                dto.plan_id
            )

            if not plan:
                raise WarrantyPlanNotFound()

            # =========================
            # OLD STATUS
            # =========================

            old_status = plan.active

            # =========================
            # DOMAIN TRANSITION
            # =========================

            if dto.active:
                plan.activate()
            else:
                plan.deactivate()

            # =========================
            # PERSISTENCE
            # =========================

            self.repository.update(plan)

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=(
                    EventType.WARRANTY_PLAN_ACTIVATED
                    if dto.active
                    else EventType.WARRANTY_PLAN_DEACTIVATED
                ),
                message=(
                    "Plan de garantie activé"
                    if dto.active
                    else "Plan de garantie désactivé"
                ),
                user_id=dto.admin_id,
                event_metadata={
                    "plan_id": plan.id,
                    "name": plan.name,
                    "old_status": old_status,
                    "new_status": dto.active,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            logger.info(
                "Statut plan de garantie modifié",
                extra={
                    "plan_id": plan.id,
                    "admin_id": dto.admin_id,
                    "old_active": old_status,
                    "new_active": dto.active,
                },
            )

            # =========================
            # RETURN DOMAIN
            # =========================

            return plan

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur modification statut plan de garantie",
                extra={
                    "plan_id": dto.plan_id,
                    "admin_id": dto.admin_id,
                    "active": dto.active,
                },
            )

            raise