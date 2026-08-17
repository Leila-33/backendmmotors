# modules/financing/application/results/create_subscription_result.py

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateSubscriptionResult:

    contract_id: str
    stripe_customer_id: str
    stripe_subscription_id: str
    subscription_status: str