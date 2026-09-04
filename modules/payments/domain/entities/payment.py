from dataclasses import dataclass
from datetime import datetime
from modules.payments.domain.enums import PaymentStatus


@dataclass
class Payment:

    id: str

    # relations
    application_id: str
    user_id: str

    # stripe
    stripe_session_id: str | None = None
    stripe_payment_intent_id: str | None = None
    stripe_customer_id: str | None = None

    # financial
    amount: float = 0.0
    currency: str = "eur"

    # status
    status: PaymentStatus = PaymentStatus.PENDING

    # metadata
    description: str | None = None

    # timestamps
    created_at: datetime | None = None
    updated_at: datetime | None = None