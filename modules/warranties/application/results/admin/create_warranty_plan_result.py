from dataclasses import dataclass


@dataclass(frozen=True)
class CreateWarrantyPlanResult:
    plan_id: str