from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from modules.core.enums import ReservationStatus


@dataclass
class Reservation:
    id: Optional[int] = None

    vehicle_id: str = 0
    user_id: str = 0

    start_date: date = None
    end_date: date = None

    status: ReservationStatus = ReservationStatus.ACTIVE

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None