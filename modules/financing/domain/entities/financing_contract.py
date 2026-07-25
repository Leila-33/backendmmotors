from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from modules.payments.domain.enums import SubscriptionStatus

@dataclass
class FinancingContract:

    id: str

    application_id: str

    financed_amount: float

    monthly_payment: float

    duration_months: int

    remaining_balance: float

    stripe_customer_id: Optional[str] = None

    stripe_subscription_id: Optional[str] = None

    subscription_status: Optional[SubscriptionStatus] = None

    created_at: Optional[datetime] = None

    updated_at: Optional[datetime] = None