from uuid import uuid4
from modules.warranties.domain.exceptions import WarrantyPlanAlreadyExists

from modules.warranties.domain.entities.warranty_plan import WarrantyPlan
from modules.warranties.api.schemas import (
    CreateWarrantyPlanRequest,
    CreateWarrantyPlanResponse
)




class CreateWarrantyPlanUseCase:


    def __init__(
        self,
        repository,
        unit_of_work
    ):
        self.repository = repository
        self.unit_of_work = unit_of_work



    def execute(
        self,
        dto: CreateWarrantyPlanRequest
    ):


        # =========================
        # CHECK DUPLICATE NAME
        # =========================
        name = (
    " ".join(
        dto.name
        .strip()
        .split()
    )
)


        existing = (
            self.repository
            .find_by_name(
                name
            )
        )


        if existing:

            raise WarrantyPlanAlreadyExists(
                "Un plan avec ce nom existe déjà"
            )



        # =========================
        # CHECK DUPLICATE TYPE
        # =========================

        existing = (
            self.repository
            .find_by_plan_type(
                dto.plan_type
            )
        )


        if existing:

            raise WarrantyPlanAlreadyExists(
                "Un plan existe déjà pour ce type"
            )



        # =========================
        # CREATE DOMAIN
        # =========================

        plan = WarrantyPlan(

            id=str(uuid4()),

            name=dto.name.strip(),

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


            active=True
        )



        # =========================
        # SAVE
        # =========================

        plan = (
            self.repository
            .save(plan)
        )



        self.unit_of_work.commit()



        # =========================
        # RESPONSE
        # =========================

        return CreateWarrantyPlanResponse(

            id=plan.id,

            message="Plan de garantie créé avec succès"

        )