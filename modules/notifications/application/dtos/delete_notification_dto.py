from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteNotificationDTO:
    notification_id: str
    user_id: str