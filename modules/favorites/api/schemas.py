from pydantic import BaseModel
from typing import List, Optional


# add favorites

class AddFavoriteResponse(BaseModel):

    id: str

    message: str

# remove favorite

class RemoveFavoriteResponse(BaseModel):

    message: str

# get favorites

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


class GetFavoritesResponse(BaseModel):
    items: List[FavoriteSchema]