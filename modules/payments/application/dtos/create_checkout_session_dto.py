# modules/payments/application/dtos/create_checkout_session_dto.py

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCheckoutSessionDTO:
    application_id: str
    user_id: str
    amount: float
    product_name: str
    email: str
    customer_name: str