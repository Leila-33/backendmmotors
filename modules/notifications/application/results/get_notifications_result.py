from dataclasses import dataclass

from modules.notifications.application.results.notification_result import (
    NotificationResult,
)


@dataclass(frozen=True)
class GetNotificationsResult:
    items: list[NotificationResult]