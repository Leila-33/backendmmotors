from dataclasses import dataclass


@dataclass
class ToggleUserActiveResult:
    id: str
    is_active: bool