from dataclasses import dataclass

from modules.vehicles.domain.enums import (
    VehicleType,
    EngineType,
    VehicleCondition,
    )


@dataclass(frozen=True)
class CreateVehicleDTO:
    brand: str
    model: str
    price: float
    type: VehicleType
    mileage: int
    year: int
    description: str | None
    engine_type: EngineType
    equipments: list[str]
    condition: VehicleCondition
    images: list[str]
    license_plate: str | None
    warranty_plan_id: str | None
    included_options: list[str]
    optional_options: list[str]