from modules.warranties.domain.exceptions import (
    WarrantyPlanNotFound,
    WarrantyPlanAlreadyExists
)
from modules.warranties.api.schemas import UpdateWarrantyPlanResponse
from modules.warranties.infrastructure.mappers.warranty_plan_mapper import WarrantyPlanMapper
from modules.applications.domain.enums import EventType
import logging

logger = logging.getLogger(__name__)

class UpdateWarrantyPlanUseCase:


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
        dto,
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
            # NORMALIZE
            # =========================

            name = dto.name.strip()


            # =========================
            # DUPLICATE NAME
            # =========================

            existing = (
                self.repository
                .find_by_name(name)
            )

            if existing and existing.id != plan.id:
                raise WarrantyPlanAlreadyExists(
                    "Plan déjà existant"
                )


            # =========================
            # DUPLICATE TYPE
            # =========================

            existing = (
                self.repository
                .find_by_plan_type(dto.plan_type)
            )

            if existing and existing.id != plan.id:
                raise WarrantyPlanAlreadyExists(
                    "Un plan existe déjà pour ce type"
                )

            old_plan = {
    "name": plan.name,
    "description": plan.description,
    "plan_type": plan.plan_type.value,
    "duration_months": plan.duration_months,
    "mileage_limit": plan.mileage_limit,
    "price": plan.price,
    "covers_engine": plan.covers_engine,
    "covers_transmission": plan.covers_transmission,
    "covers_electronics": plan.covers_electronics,
    "covers_assistance": plan.covers_assistance,
    "covers_wear_parts": plan.covers_wear_parts,
}

            # =========================
            # UPDATE
            # =========================

            plan = WarrantyPlanMapper.update_model(
                plan,
                dto,
            )
            updated_fields = []

            for field, old_value in old_plan.items():

                new_value = getattr(
                    plan,
                    field
                )

                if old_value != new_value:
                    updated_fields.append(field)
            # =========================
            # SAVE
            # =========================

            self.event_service.log(
                type=EventType.WARRANTY_PLAN_UPDATED,

                message="Plan de garantie modifié",

                user_id=current_admin.id,

                event_metadata={
                    "plan_id": plan.id,

                    "updated_fields": updated_fields,
                },
            )
            self.repository.update(plan)

            self.unit_of_work.commit()

            logger.info(
    "Plan de garantie modifié",
    extra={
        "plan_id": plan.id,
        "updated_fields": updated_fields,
    },
)
        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur modification plan de garantie",
                extra={
                    "plan_id": plan_id,
                    "updated_fields": updated_fields,
                },
            )

            raise

        # =========================
        # RESPONSE
        # =========================

        return UpdateWarrantyPlanResponse(

                id=plan.id,

                message="Plan modifié avec succès"

            )