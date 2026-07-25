from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from modules.reservations.domain.enums import ReservationStatus


@dataclass
class Reservation:

    id: str

    vehicle_id: str

    application_id: str

    start_date: date
    end_date: date

    status: ReservationStatus = ReservationStatus.ACTIVE

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None