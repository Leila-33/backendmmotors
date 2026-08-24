from dataclasses import dataclass
from typing import Optional

from modules.warranties.domain.enums import WarrantyPlanType


@dataclass(frozen=True)
class CreateWarrantyPlanDTO:
    name: str
    description: Optional[str]
    plan_type: WarrantyPlanType

    duration_months: int
    mileage_limit: Optional[int]

    covers_engine: bool
    covers_transmission: bool
    covers_electronics: bool
    covers_assistance: bool
    covers_wear_parts: bool

    price: float

    admin_id: str