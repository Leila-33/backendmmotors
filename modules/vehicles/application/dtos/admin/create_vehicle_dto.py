from dataclasses import dataclass

from modules.vehicles.domain.enums import (
    VehicleType,
    VehicleOptionType,
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
    engine_type: str
    equipments: list[str]
    condition: str
    images: list[str]
    license_plate: str | None
    warranty_plan_id: str | None
    included_options: list[str]
    optional_options: list[str]