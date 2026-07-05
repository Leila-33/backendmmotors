from modules.warranties.domain.repositories.warranty_plan_repository import WarrantyPlanRepository
from modules.warranties.infrastructure.mappers.warranty_mapper import to_domain, to_model
from modules.warranties.infrastructure.db.warranty_plan_model import WarrantyPlanModel
from modules.core.enums import WarrantyPlanType

class WarrantyPlanRepositorySQL(WarrantyPlanRepository):

    def __init__(self, session):
        self.session = session

    def save_plan(self, plan):
        model = to_model(plan)
        self.session.add(model)
        return to_domain(model)

    def find_by_name(self, name: str):
        model = (
            self.session.query(WarrantyPlanModel)
            .filter(WarrantyPlanModel.name == name)
            .first()
        )
        return to_domain(model) if model else None


    def find_by_plan_type(self, plan_type: WarrantyPlanType):
        return (
            self.session.query(WarrantyPlanModel)
            .filter(
                WarrantyPlanModel.plan_type == plan_type,
                WarrantyPlanModel.active.is_(True)
            )
            .first()
        )

    def find_all(self):
        models = (
            self.session.query(WarrantyPlanModel)
            .order_by(WarrantyPlanModel.name.asc())
            .all()
        )

        return [
            to_domain(m)
            for m in models
        ]



    def delete(self, plan_id: str):
        model = (
            self.session.query(WarrantyPlanModel)
            .filter(WarrantyPlanModel.id == plan_id)
            .first()
        )

        if model:
            self.session.delete(model)

    def commit(self):
        self.session.commit()



    def get_by_id(self, plan_id: str):

        return (
            self.session.query(WarrantyPlanModel)
            .filter(WarrantyPlanModel.id == plan_id)
            .first()
        )

    def update(self, plan):

        self.session.merge(plan)

