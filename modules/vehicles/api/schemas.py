from pydantic import BaseModel
from typing import List
from enum import Enum


class VehicleType(str, Enum):
    ACHAT = "achat"
    LOCATION = "location"


class EngineType(str, Enum):
    DIESEL = "diesel"
    ESSENCE = "essence"
    HYBRIDE = "hybride"
    ELECTRIQUE = "electrique"


class VehicleResponse(BaseModel):
    id: str
    brand: str
    model: str
    price: float
    type: VehicleType
    mileage: int
    year: int

    description: str
    engineType: EngineType
    equipments: List[str]
    condition: str

    isAvailable: bool
    images: List[str]


class VehicleSearchResponse(BaseModel):
    id: str
    brand: str
    model: str
    price: float
    type: VehicleType
    mileage: int
    year: int
    isAvailable: bool
    images: List[str]