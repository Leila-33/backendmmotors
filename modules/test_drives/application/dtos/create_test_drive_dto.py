from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateTestDriveDTO:
    vehicle_id: str
    appointment_date: datetime
    comment: str | None = None