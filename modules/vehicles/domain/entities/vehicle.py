from dataclasses import dataclass
from typing import List
from enum import Enum


class VehicleType(Enum):
    ACHAT = "achat"
    LOCATION = "location"


class EngineType(Enum):
    DIESEL = "diesel"
    ESSENCE = "essence"
    HYBRIDE = "hybride"
    ELECTRIQUE = "electrique"


@dataclass
class Vehicle:
    id: str
    brand: str
    model: str
    price: float
    type: VehicleType
    mileage: int
    year: int

    # US2 👇
    description: str
    engineType: EngineType
    equipments: List[str]
    condition: str

    isAvailable: bool
    images: List[str]