from dataclasses import dataclass


@dataclass(frozen=True)
class HandlePaymentSuccessDTO:

    stripe_session_id: str