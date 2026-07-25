from enum import Enum

# =========================
# RESERVATION
# =========================
class ReservationStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"