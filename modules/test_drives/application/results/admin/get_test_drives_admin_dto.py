from dataclasses import dataclass

from modules.test_drives.domain.enums import TestDriveStatus


@dataclass(frozen=True)
class GetTestDrivesAdminDTO:
    status: TestDriveStatus | None = None
    search: str | None = None
    page: int = 1
    limit: int = 20