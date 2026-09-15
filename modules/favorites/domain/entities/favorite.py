from dataclasses import dataclass
from datetime import datetime
from modules.vehicles.domain.entities.vehicle import Vehicle

@dataclass
class Favorite:

    # =========================
    # IDENTIFIANT
    # =========================

    id: str

    # =========================
    # RELATIONS
    # =========================

    user_id: str

    vehicle_id: str

    # =========================
    # METADATA
    # =========================

    created_at: datetime

    vehicle: Vehicle | None = None