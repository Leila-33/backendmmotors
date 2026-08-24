from dataclasses import dataclass
from typing import Optional, Literal

from modules.vehicles.domain.enums import VehicleType


@dataclass
class VehicleSearchFiltersDTO:

    page: int = 1
    size: int = 10

    sort_by: Literal[
        "price",
        "year",
        "mileage"
    ] = "year"

    order: Literal[
        "asc",
        "desc"
    ] = "desc"

    search: Optional[str] = None

    type: Optional[VehicleType] = None
    brand: Optional[str] = None
    model: Optional[str] = None

    price_min: Optional[float] = None
    price_max: Optional[float] = None

    year_min: Optional[int] = None
    mileage_max: Optional[int] = None

    is_available: Optional[bool] = None

    license_plate: Optional[str] = None