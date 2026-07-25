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