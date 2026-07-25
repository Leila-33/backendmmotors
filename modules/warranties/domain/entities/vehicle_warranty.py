from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from modules.warranties.domain.entities.warranty_plan import WarrantyPlan

@dataclass
class VehicleWarranty:
    id: str

    vehicle_id: str
    warranty_plan_id: str

    # =========================
    # INITIAL STATE (CREATION VEHICLE)
    # =========================
    is_active: bool = False

    # =========================
    # FILLED AT PAYMENT ONLY
    # =========================
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    current_mileage: int = 0
    max_mileage: Optional[int] = None
    warranty_plan: Optional["WarrantyPlan"] = None