from dataclasses import dataclass
from core.pagination.paginated_result import (
    PaginatedResult,
)
from modules.test_drives.domain.entities.test_drive import TestDrive

@dataclass
class TestDriveAdminStats:
    pending: int
    confirmed: int
    completed: int
    cancelled: int


@dataclass
class GetTestDrivesAdminResult:
    pagination: PaginatedResult[TestDrive]
    stats: TestDriveAdminStats