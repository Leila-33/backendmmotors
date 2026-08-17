from dataclasses import dataclass


@dataclass(frozen=True)
class ToggleOptionStatusResult:

    id: str
    is_active: bool
    message: str