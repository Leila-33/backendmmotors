from dataclasses import dataclass
from datetime import datetime


@dataclass
class CheckAvailabilityDTO:

    vehicle_id: str

    start_date: datetime

    end_date: datetime