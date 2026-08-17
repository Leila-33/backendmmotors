from dataclasses import dataclass


@dataclass(frozen=True)
class ToggleOptionStatusDTO:

    option_id: str
    is_active: bool
    admin_id: str