from dataclasses import dataclass

from modules.test_drives.domain.entities.test_drive import TestDrive


@dataclass(frozen=True)
class GetMyTestDrivesResult:
    items: list[TestDrive]