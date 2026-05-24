from dataclasses import dataclass, field
from typing import List, Optional

from modules.core.enums import VehicleCondition, VehicleType, EngineType
# =========================
# ENTITY
# =========================

from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses import dataclass, field
from typing import List, Optional

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

    images: List[str] = field(default_factory=list)

    # 🚗 NEW FIELD
    license_plate: Optional[str] = None