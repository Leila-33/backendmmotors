from enum import Enum

class TicketStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_CUSTOMER = "WAITING_CUSTOMER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class TicketPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class TicketCategory(str, Enum):
    GENERAL = "GENERAL"
    FINANCING = "FINANCING"
    DELIVERY = "DELIVERY"
    WARRANTY = "WARRANTY"
    VEHICLE_ISSUE = "VEHICLE_ISSUE"
    DOCUMENTS = "DOCUMENTS"
    PAYMENT = "PAYMENT"
    OTHER = "OTHER"

class TicketFilter(str, Enum):
    ALL = "all"
    OPEN = "open"
    URGENT = "urgent"