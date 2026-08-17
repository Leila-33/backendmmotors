# modules/payments/application/dtos/create_checkout_session_dto.py

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateCheckoutSessionDTO:

    application_id: str
    user_id: str

    amount: Decimal
    product_name: str
    email: str