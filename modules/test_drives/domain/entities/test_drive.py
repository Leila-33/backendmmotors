from dataclasses import dataclass
from datetime import datetime
from modules.core.enums import TestDriveStatus


@dataclass
class TestDrive:

    id: str

    user_id: str

    vehicle_id: str

    appointment_date: datetime

    status: TestDriveStatus

    comment: str | None = None

    created_at: datetime | None = None