from modules.notifications.application.dtos.get_notifications_dto import (
    GetNotificationsDTO,
)

from modules.notifications.application.results.get_notifications_result import (
    GetNotificationsResult,
)

from modules.notifications.application.results.notification_result import (
    NotificationResult,
)


class GetNotificationsUseCase:

    def __init__(
        self,
        notification_repository,
    ):
        self.notification_repository = (
            notification_repository
        )

    def execute(
        self,
        dto: GetNotificationsDTO,
    ) -> GetNotificationsResult:

        notifications = (
            self.notification_repository
            .get_by_user(
                dto.user_id
            )
        )
    
        return GetNotificationsResult(
            items=[
                NotificationResult(
                    id=notification.id,
                    title=notification.title,
                    message=notification.message,
                    type=notification.type.value,
                    status=notification.status.value,
                    created_at=notification.created_at,
                    entity_type=(
                        notification.entity_type.value
                        if notification.entity_type
                        else None
                    ),
                    entity_id=notification.entity_id,
                )
                for notification in notifications
            ]
        )