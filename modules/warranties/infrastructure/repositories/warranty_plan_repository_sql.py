from sqlalchemy import func
from sqlalchemy.orm import Session

from modules.warranties.domain.entities.warranty_plan import WarrantyPlan
from modules.warranties.domain.enums import WarrantyPlanType
from modules.warranties.domain.repositories.warranty_plan_repository import (
    WarrantyPlanRepository,
)
from modules.warranties.infrastructure.db.warranty_plan_model import (
    WarrantyPlanModel,
)
from modules.warranties.infrastructure.mappers.warranty_plan_mapper import (
    WarrantyPlanMapper,
)


class WarrantyPlanRepositorySQL(WarrantyPlanRepository):

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    # =====================================================
    # CREATE
    # =====================================================

    def save(
        self,
        plan: WarrantyPlan,
    ) -> WarrantyPlan:

        model = WarrantyPlanMapper.to_model(plan)

        self.db.add(model)

        self.db.flush()

        return WarrantyPlanMapper.to_domain(model)

    # =====================================================
    # FIND BY NAME
    # =====================================================

    def find_by_name(
        self,
        name: str,
    ) -> WarrantyPlan | None:

        normalized_name = " ".join(
            name.strip().split()
        )

        model = (
            self.db
            .query(WarrantyPlanModel)
            .filter(
                func.lower(
                    WarrantyPlanModel.name
                )
                == normalized_name.lower()
            )
            .first()
        )

        if model is None:
            return None

        return WarrantyPlanMapper.to_domain(model)

    # =====================================================
    # FIND ALL
    # =====================================================

    def find_all(
        self,
    ) -> list[WarrantyPlan]:

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

    # =====================================================
    # FIND BY TYPE
    # =====================================================

    def find_by_plan_type(
        self,
        plan_type: WarrantyPlanType,
    ) -> WarrantyPlan | None:

        model = (
            self.db
            .query(WarrantyPlanModel)
            .filter(
                WarrantyPlanModel.plan_type == plan_type
            )
            .first()
        )

        if model is None:
            return None

        return WarrantyPlanMapper.to_domain(model)

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        plan_id: str,
    ) -> WarrantyPlan | None:

        model = (
            self.db
            .query(WarrantyPlanModel)
            .filter(
                WarrantyPlanModel.id == plan_id
            )
            .first()
        )

        if model is None:
            return None

        return WarrantyPlanMapper.to_domain(model)

    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        plan: WarrantyPlan,
    ) -> WarrantyPlan | None:

        model = (
            self.db
            .query(WarrantyPlanModel)
            .filter(
                WarrantyPlanModel.id == plan.id
            )
            .first()
        )

        if model is None:
            return None

        WarrantyPlanMapper.update_model(
            model,
            plan,
        )

        self.db.flush()

        return WarrantyPlanMapper.to_domain(model)

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        plan_id: str,
    ) -> bool:

        model = (
            self.db
            .query(WarrantyPlanModel)
            .filter(
                WarrantyPlanModel.id == plan_id
            )
            .first()
        )

        if model is None:
            return False

        self.db.delete(model)

        self.db.flush()

        return True