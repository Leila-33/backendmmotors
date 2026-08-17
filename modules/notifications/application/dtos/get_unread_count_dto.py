from dataclasses import dataclass


@dataclass(frozen=True)
class GetUnreadCountDTO:
    user_id: str