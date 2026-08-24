from dataclasses import dataclass


@dataclass(frozen=True)
class ToggleWarrantyPlanDTO:
    plan_id: str
    active: bool
    admin_id: str