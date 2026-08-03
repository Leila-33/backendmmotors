from enum import Enum


class InstallmentStatus(str, Enum):

    PENDING = "pending"

    PAID = "paid"

    FAILED = "failed"

    CANCELLED = "cancelled"