from dataclasses import dataclass


@dataclass(frozen=True)
class GetAvailabilityResult:
    date: str
    timezone: str
    available_slots: list[str]