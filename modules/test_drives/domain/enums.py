from enum import Enum

class TestDriveStatus(str, Enum):

    PENDING = "pending"

    CONFIRMED = "confirmed"
    REJECTED = "rejected"

    CANCELLED = "cancelled"

    COMPLETED = "completed"