from modules.warranties.domain.repositories.warranty_plan_repository import WarrantyPlanRepository
from modules.warranties.infrastructure.mappers.warranty_plan_mapper import WarrantyPlanMapper
from modules.warranties.infrastructure.db.warranty_plan_model import WarrantyPlanModel
from sqlalchemy.orm import Session
from sqlalchemy import func




class WarrantyPlanRepositorySQL(WarrantyPlanRepository):


    def __init__(
        self,
        db: Session
    ):
        self.db = db



    # =========================
    # CREATE
    # =========================

    def save(
        self,
        plan
    ):

        try:

            model = (
                WarrantyPlanMapper
                .to_model(plan)
            )

            self.db.add(model)

            self.db.commit()

            self.db.refresh(model)


            return (
                WarrantyPlanMapper
                .to_domain(model)
            )


        except Exception:

            self.db.rollback()

            raise



    # =========================
    # FIND BY NAME
    # =========================

    def find_by_name(
        self,
        name: str
    ):

        model = (
            self.db
        .query(WarrantyPlanModel)
        .filter(
            func.lower(
                WarrantyPlanModel.name
            )
            ==
            name.lower()
        )
        .first()
        )


        if not model:
            return None


        return (
            WarrantyPlanMapper
            .to_domain(model)
        )



    # =========================
    # FIND ALL
    # =========================

    def find_all(
        self
    ):

        models = (
            self.db
            .query(WarrantyPlanModel)
            .order_by(
                WarrantyPlanModel.name.asc()
            )
            .all()
        )


        return [
            WarrantyPlanMapper.to_domain(model)
            for model in models
        ]



    # =========================
    # FIND BY TYPE
    # =========================

    def find_by_plan_type(
        self,
        plan_type: str
    ):

        model = (
            self.db
            .query(WarrantyPlanModel)
            .filter(
                WarrantyPlanModel.plan_type == plan_type
            )
            .first()
        )

        if not model:
            return None

        return WarrantyPlanMapper.to_domain(model)



    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        plan_id: str
    ):


        model = (
            self.db
            .query(WarrantyPlanModel)
            .filter(
                WarrantyPlanModel.id == plan_id
            )
            .first()
        )


        if not model:
            return None


        return (
            WarrantyPlanMapper
            .to_domain(model)
        )



    # =========================
    # UPDATE
    # =========================

    def update(
        self,
        plan
    ):


        model = (
            self.db
            .query(WarrantyPlanModel)
            .filter(
                WarrantyPlanModel.id == plan.id
            )
            .first()
        )


        if not model:
            return None



        WarrantyPlanMapper.update_model(
            model,
            plan
        )


        self.db.commit()

        self.db.refresh(model)


        return (
            WarrantyPlanMapper
            .to_domain(model)
        )



    # =========================
    # DELETE
    # =========================

    def delete(
        self,
        plan_id: str
    ):


        model = (
            self.db
            .query(WarrantyPlanModel)
            .filter(
                WarrantyPlanModel.id == plan_id
            )
            .first()
        )


        if not model:
            return None


        self.db.delete(model)

        self.db.commit()


        return True
