from uuid import uuid4
import logging

from modules.warranties.domain.exceptions import (
    WarrantyPlanAlreadyExists,
)
from modules.warranties.domain.entities.warranty_plan import (
    WarrantyPlan,
)
from modules.applications.domain.enums import EventType

from modules.warranties.application.dtos.admin.create_warranty_plan_dto import (
    CreateWarrantyPlanDTO,
)

from modules.warranties.application.results.admin.create_warranty_plan_result import (
    CreateWarrantyPlanResult,
)


logger = logging.getLogger(__name__)


class CreateWarrantyPlanUseCase:

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
        dto: CreateWarrantyPlanDTO,
    ) -> CreateWarrantyPlanResult:

        try:

            # =====================================================
            # NORMALIZE NAME
            # =====================================================

            name = " ".join(
                dto.name.strip().split()
            )

            # =====================================================
            # CHECK DUPLICATE NAME
            # =====================================================

            existing = self.repository.find_by_name(
                name
            )

            if existing:
                raise WarrantyPlanAlreadyExists(
                    "Un plan avec ce nom existe déjà"
                )

            # =====================================================
            # CHECK DUPLICATE TYPE
            # =====================================================

            existing = self.repository.find_by_plan_type(
                dto.plan_type
            )

            if existing:
                raise WarrantyPlanAlreadyExists(
                    "Un plan existe déjà pour ce type"
                )

            # =====================================================
            # CREATE DOMAIN
            # =====================================================

            plan = WarrantyPlan(
                id=str(uuid4()),

                name=name,
                description=dto.description,

                plan_type=dto.plan_type,

                duration_months=dto.duration_months,
                mileage_limit=dto.mileage_limit,

                covers_engine=dto.covers_engine,
                covers_transmission=dto.covers_transmission,
                covers_electronics=dto.covers_electronics,
                covers_assistance=dto.covers_assistance,
                covers_wear_parts=dto.covers_wear_parts,

                price=dto.price,

                active=True,
            )

            # =====================================================
            # SAVE
            # =====================================================

            self.repository.save(plan)

            # =====================================================
            # EVENT
            # =====================================================

            self.event_service.log(
                type=EventType.WARRANTY_PLAN_CREATED,
                message="Plan de garantie créé",
                user_id=dto.admin_id,
                event_metadata={
                    "plan_id": plan.id,
                    "name": plan.name,
                    "plan_type": plan.plan_type.value,
                    "duration_months": plan.duration_months,
                    "mileage_limit": plan.mileage_limit,
                    "price": plan.price,
                    "coverage": {
                        "engine": plan.covers_engine,
                        "transmission": plan.covers_transmission,
                        "electronics": plan.covers_electronics,
                        "assistance": plan.covers_assistance,
                        "wear_parts": plan.covers_wear_parts,
                    },
                    "active": plan.active,
                },
            )

            # =====================================================
            # COMMIT
            # =====================================================

            self.unit_of_work.commit()

            logger.info(
                "Plan de garantie créé",
                extra={
                    "plan_id": plan.id,
                    "admin_id": dto.admin_id,
                    "plan_type": plan.plan_type.value,
                },
            )

            # =====================================================
            # RESULT
            # =====================================================

            return CreateWarrantyPlanResult(
                plan_id=plan.id
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création plan de garantie",
                extra={
                    "plan_name": dto.name,
                    "admin_id": dto.admin_id,
                    "plan_type": (
                        dto.plan_type.value
                        if dto.plan_type
                        else None
                    ),
                },
            )

            raise