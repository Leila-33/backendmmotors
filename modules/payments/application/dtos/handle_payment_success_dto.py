from dataclasses import dataclass


@dataclass(frozen=True)
class HandlePaymentSuccessDTO:
    stripe_session_id: str
    stripe_payment_intent_id: str | None