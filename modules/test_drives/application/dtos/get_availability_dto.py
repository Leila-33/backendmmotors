from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class GetAvailabilityDTO:
    vehicle_id: str
    date: date