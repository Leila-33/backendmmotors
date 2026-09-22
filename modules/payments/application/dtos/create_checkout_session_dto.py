from dataclasses import dataclass


@dataclass
class CreateCheckoutSessionDTO:

    application_id: str
    user_id: str