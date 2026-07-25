from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class InstallmentStatus(Enum):

    PENDING = "PENDING"

    PAID = "PAID"

    FAILED = "FAILED"

    LATE = "LATE"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    COMPLETED = "completed"