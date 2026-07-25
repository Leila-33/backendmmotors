from dataclasses import dataclass
from datetime import datetime


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

    vehicle: object | None = None