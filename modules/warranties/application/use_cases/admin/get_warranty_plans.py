class GetWarrantyPlansUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self):

        plans = self.repository.find_all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,

                "plan_type": p.plan_type.value if hasattr(p.plan_type, "value") else p.plan_type,

                "duration_months": p.duration_months,
                "mileage_limit": p.mileage_limit,

                "covers_engine": p.covers_engine,
                "covers_transmission": p.covers_transmission,
                "covers_electronics": p.covers_electronics,
                "covers_assistance": p.covers_assistance,
                "covers_wear_parts": p.covers_wear_parts,

                "deductible": p.deductible,
                "price": p.price,
                "active": p.active
            }
            for p in plans
        ]