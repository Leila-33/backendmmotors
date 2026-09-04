# modules/financing/application/dtos/handle_subscription_payment_dto.py

from dataclasses import dataclass


@dataclass(frozen=True)
class HandleSubscriptionPaymentDTO:

    event_type: str
    invoice_id: str
    subscription_id: str | None