from dataclasses import dataclass


@dataclass(frozen=True)
class GetNotificationsDTO:
    user_id: str