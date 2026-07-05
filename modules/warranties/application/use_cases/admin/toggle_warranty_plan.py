from modules.core.exceptions import WarrantyPlanNotFound

class ToggleWarrantyPlanUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, plan_id: str, active: bool):

        plan = self.repository.get_by_id(plan_id)

        if not plan:
            raise WarrantyPlanNotFound()

        plan.active = active

        self.repository.update(plan)
        self.repository.commit()

        return plan