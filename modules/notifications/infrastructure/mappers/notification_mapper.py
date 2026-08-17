from modules.notifications.domain.entities.notification import (
    Notification,
)
from modules.notifications.domain.enums import (
    NotificationStatus,
    NotificationType,
    NotificationEntityType
)

from modules.notifications.infrastructure.db.notification_model import (
    NotificationModel,
)

from modules.notifications.api.schemas import (
    NotificationResponse,
    GetNotificationsResponse,
    UnreadNotificationCountResponse,
    MarkNotificationReadResponse,
    DeleteNotificationResponse
)


class NotificationMapper:


    # =====================
    # DOMAIN -> MODEL
    # =====================

    @staticmethod
    def to_model(
        notification: Notification,
    ) -> NotificationModel:

        return NotificationModel(

            id=notification.id,

            user_id=notification.user_id,

            title=notification.title,

            message=notification.message,

            type=notification.type.value,

            status=notification.status.value,

            created_at=notification.created_at,

            entity_type=notification.entity_type.value,

            entity_id=notification.entity_id,

        )


    # =====================
    # MODEL -> DOMAIN
    # =====================

    @staticmethod
    def to_domain(
        model: NotificationModel,
    ) -> Notification:

        return Notification(

            id=model.id,

            user_id=model.user_id,

            title=model.title,

            message=model.message,

            type=NotificationType(
                model.type
            ),

            status=NotificationStatus(
                model.status
            ),

            created_at=model.created_at,

            entity_type=NotificationEntityType(
                model.entity_type),

            entity_id=model.entity_id,

        )


    # =====================
    # UPDATE MODEL
    # =====================

    @staticmethod
    def update_model(
        model: NotificationModel,
        notification: Notification,
    ) -> None:

        model.title = (
            notification.title
        )

        model.message = (
            notification.message
        )

        model.type = (
            notification.type.value
        )

        model.status = (
            notification.status.value
        )

        model.entity_type = (
            notification.entity_type.value
        )

        model.entity_id = (
            notification.entity_id
        )

    @staticmethod
    def to_response(
        notification
    ) -> NotificationResponse:

        return NotificationResponse(
            id=notification.id,
            title=notification.title,
            message=notification.message,
            type=notification.type,
            status=notification.status,
            created_at=notification.created_at,
            entity_type=notification.entity_type,
            entity_id=notification.entity_id,
        )

    def to_list_response(
        result,
    ) -> GetNotificationsResponse:

        return GetNotificationsResponse(
            items=[
                NotificationMapper.to_response(
                    notification
                )
                for notification in result.items
            ]
        )

    @staticmethod
    def to_unread_count_response(
        result,
    ) -> UnreadNotificationCountResponse:

        return UnreadNotificationCountResponse(
            count=result.count
        )

    @staticmethod
    def to_mark_read_response(
        result,
    ) -> MarkNotificationReadResponse:

        return MarkNotificationReadResponse(
            success=result.success,
            message=result.message,
        )

    @staticmethod
    def to_delete_response(
        result,
    ) -> DeleteNotificationResponse:

        return DeleteNotificationResponse(
            id=result.id,
            success=result.success,
            message=result.message,
        )