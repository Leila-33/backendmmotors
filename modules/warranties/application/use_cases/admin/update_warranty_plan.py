import logging

from modules.warranties.domain.exceptions import (
    WarrantyPlanNotFound,
    WarrantyPlanAlreadyExists,
)
from modules.applications.domain.enums import EventType
from modules.warranties.application.dtos.admin.update_warranty_plan_dto import (
    UpdateWarrantyPlanDTO,
)

logger = logging.getLogger(__name__)


class UpdateWarrantyPlanUseCase:
    """
    Modifie un plan de garantie après vérification de son existence
    et de l'unicité de son nom et de son type.

    Les champs modifiés sont détectés et enregistrés dans l'historique
    des événements.
    """
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
        dto: UpdateWarrantyPlanDTO,
    ):

        updated_fields = []

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
            # NORMALIZE NAME
            # =========================

            name = (
                " ".join(
                    dto.name
                    .strip()
                    .split()
                )
            )

            # =========================
            # DUPLICATE NAME
            # =========================

            existing = self.repository.find_by_name(
                name
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
                .find_by_plan_type(
                    dto.plan_type
                )
            )

            if existing and existing.id != plan.id:
                raise WarrantyPlanAlreadyExists(
                    "Un plan existe déjà pour ce type"
                )

            # =========================
            # OLD VALUES
            # =========================

            old_values = {
                "name": plan.name,
                "description": plan.description,
                "plan_type": plan.plan_type,
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
            # UPDATE DOMAIN
            # =========================

            plan.name = name
            plan.description = dto.description
            plan.plan_type = dto.plan_type
            plan.duration_months = dto.duration_months
            plan.mileage_limit = dto.mileage_limit

            plan.price = dto.price

            plan.covers_engine = dto.covers_engine
            plan.covers_transmission = (
                dto.covers_transmission
            )
            plan.covers_electronics = (
                dto.covers_electronics
            )
            plan.covers_assistance = (
                dto.covers_assistance
            )
            plan.covers_wear_parts = (
                dto.covers_wear_parts
            )

            # =========================
            # DETECT CHANGES
            # =========================

            for field, old_value in old_values.items():

                new_value = getattr(
                    plan,
                    field,
                )

                if old_value != new_value:
                    updated_fields.append(field)

            # =========================
            # SAVE
            # =========================

            self.repository.update(plan)

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.WARRANTY_PLAN_UPDATED,
                message="Plan de garantie modifié",
                user_id=dto.admin_id,
                event_metadata={
                    "plan_id": plan.id,
                    "updated_fields": updated_fields,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            logger.info(
                "Plan de garantie modifié",
                extra={
                    "plan_id": plan.id,
                    "admin_id": dto.admin_id,
                    "updated_fields": updated_fields,
                },
            )

            # =========================
            # RETURN DOMAIN
            # =========================

            return plan

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur modification plan de garantie",
                extra={
                    "plan_id": dto.plan_id,
                    "admin_id": dto.admin_id,
                    "updated_fields": updated_fields,
                },
            )

            raise