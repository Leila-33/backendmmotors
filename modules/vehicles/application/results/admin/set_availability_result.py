from dataclasses import dataclass

@dataclass(frozen=True)
class SetAvailabilityResult:
    vehicle_id: str
    status: str
    is_available: bool
    message: str