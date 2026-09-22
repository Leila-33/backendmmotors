from dataclasses import dataclass
from typing import Literal

from modules.vehicles.domain.enums import (
    VehicleType,
    EngineType
)

@dataclass
class VehicleSearchFiltersDTO:

    # =========================
    # PAGINATION
    # =========================

    page: int = 1
    size: int = 10

    # =========================
    # TRI
    # =========================

    sort_by: Literal[
        "price",
        "year",
        "mileage",
    ] = "year"

    order: Literal[
        "asc",
        "desc",
    ] = "desc"

    # =========================
    # FILTRES COMMUNS
    # =========================

    type: VehicleType | None = None

    # =========================
    # FILTRES CLIENT
    # =========================

    brand: str | None = None
    model: str | None = None

    engine_type: EngineType | None = None

    price_min: float | None = None
    price_max: float | None = None

    year_min: int | None = None
    mileage_max: int | None = None

    # =========================
    # FILTRES ADMIN
    # =========================

    search: str | None = None
    license_plate: str | None = None

    # =========================
    # RÈGLE INTERNE
    # =========================

    # Ce champ n'est pas exposé
    # directement par le frontend client.
    is_available: bool | None = None