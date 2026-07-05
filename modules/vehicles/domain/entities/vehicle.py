from dataclasses import dataclass, field
from typing import List, Optional
from modules.warranties.domain.entities.vehicle_warranty import VehicleWarranty
from modules.core.enums import VehicleCondition, VehicleType, EngineType, VehicleStatus
from datetime import datetime




@dataclass
class Vehicle:
    id: str

    brand: str
    model: str
    price: float

    type: VehicleType

    mileage: int
    year: int

    description: Optional[str] = None

    engine_type: Optional[EngineType] = None

    equipments: List[str] = field(default_factory=list)

    condition: VehicleCondition = VehicleCondition.USED

    is_available: bool = True
    
    published_at: Optional[str] = None

    images: List[str] = field(default_factory=list)

    # 🚗 NEW FIELD
    license_plate: Optional[str] = None

    warranty: Optional[VehicleWarranty] = None
    status: VehicleStatus = VehicleStatus.AVAILABLE
    final_check_at: Optional[datetime] = None