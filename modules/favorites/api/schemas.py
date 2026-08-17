from datetime import datetime

from pydantic import BaseModel

from modules.vehicles.domain.enums import VehicleType


# ============================================================
# ADD FAVORITE
# ============================================================

class AddFavoriteResponse(BaseModel):
    id: str
    message: str


# ============================================================
# REMOVE FAVORITE
# ============================================================

class RemoveFavoriteResponse(BaseModel):
    message: str


# ============================================================
# GET FAVORITES
# ============================================================

class FavoriteVehicleResponse(BaseModel):
    id: str
    brand: str
    model: str
    year: int
    price: float
    mileage: int
    type: VehicleType
    images: list[str]


class FavoriteItemResponse(BaseModel):
    id: str
    created_at: datetime | None
    vehicle: FavoriteVehicleResponse


class GetFavoritesResponse(BaseModel):
    items: list[FavoriteItemResponse]