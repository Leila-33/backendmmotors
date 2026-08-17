from dataclasses import dataclass
from datetime import datetime
from modules.vehicles.domain.enums import VehicleType


@dataclass
class FavoriteVehicleResult:
    id: str
    brand: str
    model: str
    year: int
    price: float
    mileage: int
    type: VehicleType
    images: list[str]


@dataclass
class FavoriteItemResult:
    id: str
    created_at: datetime | None
    vehicle: FavoriteVehicleResult


@dataclass
class GetFavoritesResult:
    items: list[FavoriteItemResult]