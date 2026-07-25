from enum import Enum 

class QuoteRefusalReason(str, Enum):

    PRICE = "PRICE"

    MONTHLY_PAYMENT = "MONTHLY_PAYMENT"

    FINANCING = "FINANCING"

    VEHICLE = "VEHICLE"

    PURCHASE_ELSEWHERE = "PURCHASE_ELSEWHERE"

    OTHER = "OTHER"

class QuoteStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"