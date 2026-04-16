from pydantic import BaseModel, Field
from typing import List
from enum import Enum
from typing import Optional
from modules.vehicles.domain.entities.vehicle import VehicleType


class VehicleType(str, Enum):
    ACHAT = "achat"
    LOCATION = "location"


class EngineType(str, Enum):
    DIESEL = "diesel"
    ESSENCE = "essence"
    HYBRIDE = "hybride"
    ELECTRIQUE = "electrique"





class VehicleSearchRequest(BaseModel):
    type: Optional[VehicleType] = None
    brand: Optional[str] = Field(None, min_length=1)
    model: Optional[str] = None
    engine_type: Optional[str] = None

    year: Optional[int] = None
    mileage: Optional[int] = None

    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)

    is_available: Optional[bool] = None




class VehicleResponse(BaseModel):
    id: str
    brand: str
    model: str
    price: float
    type: VehicleType
    mileage: int
    year: int

    description: str
    engine_type: EngineType
    equipments: List[str]
    condition: str

    is_available: bool
    images: List[str]

    model_config = {
        "from_attributes": True
    }


class VehicleSearchResponse(BaseModel):
    id: str
    brand: str
    model: str
    price: float
    type: VehicleType
    mileage: int
    year: int
    is_available: bool
    images: List[str]