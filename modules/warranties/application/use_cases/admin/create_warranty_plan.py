from uuid import uuid4
from datetime import datetime, timezone

from modules.core.exceptions import WarrantyPlanAlreadyExists

from modules.warranties.domain.entities.warranty_plan import WarrantyPlan
from modules.warranties.api.schemas import CreateWarrantyPlanDTO, CreateWarrantyPlanResponseDTO

class CreateWarrantyPlanUseCase:

    def __init__(self, repository):
        self.repository = repository  # 👈 interface

    def execute(self, dto: CreateWarrantyPlanDTO):

        # =========================
        # CHECK DUPLICATE
        # =========================
        existing = self.repository.find_by_name(dto.name)

        if existing:
            raise WarrantyPlanAlreadyExists(
                "Plan déjà existant"
            )
        
        existing = self.repository.find_by_plan_type(dto.plan_type)

        if existing:
            raise WarrantyPlanAlreadyExists(
                "Un plan existe déjà pour ce type"
            )

        # =========================
        # DOMAIN
        # =========================
        plan = WarrantyPlan(
            id=str(uuid4()),
            name=dto.name,
            description=dto.description,
            plan_type=dto.plan_type,
            duration_months=dto.duration_months,
            mileage_limit=dto.mileage_limit,
            covers_engine=dto.covers_engine,
            covers_transmission=dto.covers_transmission,
            covers_electronics=dto.covers_electronics,
            covers_assistance=dto.covers_assistance,
            covers_wear_parts=dto.covers_wear_parts,
            deductible=dto.deductible,
            price=dto.price,
            active=True,
        )

        # =========================
        # SAVE
        # =========================
        self.repository.save_plan(plan)
        self.repository.commit()

        # =========================
        # RESPONSE
        # =========================
        return CreateWarrantyPlanResponseDTO(
            id=plan.id,
            name=plan.name,
            price=plan.price,
            active=plan.active
        )