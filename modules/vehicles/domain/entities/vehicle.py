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
    def __init__(
        self,
        id: str,
        brand: str,
        model: str,
        price: float,
        type,
        mileage: int,
        year: int,
        description: str,
        engine_type,
        equipments,
        condition: str,
        is_available: bool,
        images
    ):
        self.id = id
        self.brand = brand
        self.model = model
        self.price = price
        self.type = type
        self.mileage = mileage
        self.year = year
        self.description = description
        self.engine_type = engine_type
        self.equipments = equipments
        self.condition = condition
        self.is_available = is_available
        self.images = images