from pydantic import BaseModel
from typing import List, Optional


class FavoriteVehicleSchema(BaseModel):
    id: str
    brand: str
    model: str
    year: int
    price: float
    mileage: int
    type: str
    images: List[str] = []


class FavoriteSchema(BaseModel):
    id: str
    created_at: Optional[str]

    vehicle: FavoriteVehicleSchema

from typing import List


class GetFavoritesResponse(BaseModel):
    items: List[FavoriteSchema]