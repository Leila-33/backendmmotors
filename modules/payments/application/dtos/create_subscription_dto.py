from dataclasses import dataclass


@dataclass(frozen=True)
class CreateSubscriptionDTO:
    contract_id: str
    stripe_customer_id: str
    user_id: str