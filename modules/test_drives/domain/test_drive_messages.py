
from modules.test_drives.domain.enums import TestDriveStatus
from modules.applications.domain.enums import EventType

TEST_DRIVE_EVENT_MAP = {
    TestDriveStatus.CONFIRMED: EventType.TEST_DRIVE_CONFIRMED,
    TestDriveStatus.REJECTED: EventType.TEST_DRIVE_REJECTED,
    TestDriveStatus.CANCELLED: EventType.TEST_DRIVE_CANCELLED,
    TestDriveStatus.COMPLETED: EventType.TEST_DRIVE_COMPLETED,
}

TEST_DRIVE_STATUS_LABELS = {
    TestDriveStatus.PENDING: "En attente",
    TestDriveStatus.CONFIRMED: "Confirmé",
    TestDriveStatus.REJECTED: "Refusé",
    TestDriveStatus.CANCELLED: "Annulé",
    TestDriveStatus.COMPLETED: "Terminé",
}