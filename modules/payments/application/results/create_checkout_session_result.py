# modules/payments/application/results/create_checkout_session_result.py

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateCheckoutSessionResult:

    checkout_url: str | None
    payment_id: str