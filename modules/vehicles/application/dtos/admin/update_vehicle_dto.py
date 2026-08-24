from dataclasses import dataclass
from typing import Optional

from modules.vehicles.domain.enums import (
    VehicleType,
    EngineType,
    VehicleCondition,
)


@dataclass
class UpdateVehicleDTO:

    vehicle_id: str
    admin_id: str

    brand: Optional[str] = None
    model: Optional[str] = None
    price: Optional[float] = None
    type: Optional[VehicleType] = None
    mileage: Optional[int] = None
    year: Optional[int] = None
    description: Optional[str] = None
    engine_type: Optional[EngineType] = None
    equipments: Optional[list[str]] = None
    condition: Optional[VehicleCondition] = None
    images: Optional[list[str]] = None
    license_plate: Optional[str] = None
    warranty_plan_id: Optional[str] = None
    included_options: Optional[list[str]] = None
    optional_options: Optional[list[str]] = None