from dataclasses import dataclass
from datetime import datetime
from modules.test_drives.domain.enums import TestDriveStatus
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.auth.domain.entities.user import User

@dataclass
class TestDrive:

    id: str

    user_id: str

    vehicle_id: str

    appointment_date: datetime

    status: TestDriveStatus

    comment: str | None = None

    created_at: datetime | None = None

    vehicle : Vehicle | None = None

    user : User | None = None