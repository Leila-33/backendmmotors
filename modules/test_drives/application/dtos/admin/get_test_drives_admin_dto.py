from dataclasses import dataclass
from modules.test_drives.domain.enums import TestDriveStatus

@dataclass
class GetTestDrivesAdminDTO:

    status: TestDriveStatus | None = None
    search: str | None = None

    # today / week / month
    date: str | None = None

    # Colonne utilisée pour le tri
    sort_by: str = "appointment_date"

    # asc / desc
    sort_order: str = "asc"

    page: int = 1
    limit: int = 20
