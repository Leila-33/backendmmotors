from modules.warranties.domain.exceptions import (
    WarrantyPlanNotFound,
    WarrantyPlanAlreadyExists
)
from modules.warranties.api.schemas import UpdateWarrantyPlanResponse
from modules.warranties.infrastructure.mappers.warranty_plan_mapper import WarrantyPlanMapper


class UpdateWarrantyPlanUseCase:


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
        dto,
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


        # =========================
        # UPDATE
        # =========================

        plan = WarrantyPlanMapper.update_model(
            plan,
            dto,
        )


        # =========================
        # SAVE
        # =========================

        self.repository.update(plan)

        self.unit_of_work.commit()


        # =========================
        # RESPONSE
        # =========================

        return UpdateWarrantyPlanResponse(

            id=plan.id,

            message="Plan modifié avec succès"

        )