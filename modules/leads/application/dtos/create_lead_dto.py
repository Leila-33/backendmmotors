from dataclasses import dataclass


@dataclass(frozen=True)
class CreateLeadDTO:
    vehicle_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    message: str
    user_id: str | None = None