from dataclasses import dataclass


@dataclass(frozen=True)
class SetAvailabilityDTO:
    vehicle_id: str
    admin_id: str
    value: bool