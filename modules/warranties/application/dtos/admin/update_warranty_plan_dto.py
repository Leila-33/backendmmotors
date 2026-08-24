from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateWarrantyPlanDTO:
    plan_id: str
    name: str
    description: str | None
    plan_type: object
    duration_months: int
    mileage_limit: int | None

    covers_engine: bool
    covers_transmission: bool
    covers_electronics: bool
    covers_assistance: bool
    covers_wear_parts: bool

    price: float
    admin_id: str