from dataclasses import dataclass

from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.applications.domain.entities.event import Event


@dataclass(frozen=True)
class GetTestDriveDetailsResult:
    test_drive: TestDrive
    events: list[Event]