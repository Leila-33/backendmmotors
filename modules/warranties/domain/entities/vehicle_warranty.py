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

    def activate(
        self,
        start_date: datetime,
        end_date: datetime,
        current_mileage: int,
        max_mileage: int,
    ):

        if self.is_active:
            return

        self.is_active = True

        self.start_date = start_date

        self.end_date = end_date

        self.current_mileage = current_mileage

        self.max_mileage = max_mileage