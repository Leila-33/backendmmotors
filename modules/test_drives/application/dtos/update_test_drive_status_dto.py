from dataclasses import dataclass

from modules.auth.domain.enums import UserRole
from modules.test_drives.domain.enums import TestDriveStatus


@dataclass(frozen=True)
class UpdateTestDriveStatusDTO:
    test_drive_id: str
    status: TestDriveStatus
    actor_id: str
    actor_role: UserRole