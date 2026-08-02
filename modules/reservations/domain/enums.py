from enum import Enum

# =========================
# RESERVATION
# =========================
class ReservationStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"