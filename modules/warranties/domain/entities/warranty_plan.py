from dataclasses import dataclass
from typing import Optional

from modules.core.enums import WarrantyPlanType


@dataclass
class WarrantyPlan:
    id: str

    name: str
    description: Optional[str]

    plan_type: WarrantyPlanType

    duration_months: int
    mileage_limit: Optional[int]  # None = illimité

    covers_engine: bool = True
    covers_transmission: bool = True
    covers_electronics: bool = False
    covers_assistance: bool = False
    covers_wear_parts: bool = False

    deductible: float = 0.0
    price: float = 0.0

    active: bool = True