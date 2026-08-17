from dataclasses import dataclass


@dataclass(frozen=True)
class CreateSubscriptionDTO:

    contract_id: str
    customer_email: str
    customer_name: str
    user_id: str