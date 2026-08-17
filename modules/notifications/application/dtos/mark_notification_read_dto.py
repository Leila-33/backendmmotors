from dataclasses import dataclass


@dataclass(frozen=True)
class MarkNotificationReadDTO:
    notification_id: str
    user_id: str