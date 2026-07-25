from modules.notifications.api.schemas import (
    NotificationResponse
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
        user_id: str,
    ):


        # =========================
        # GET NOTIFICATIONS
        # =========================

        notifications = (
            self.notification_repository
            .get_by_user(
                user_id
            )
        )


        # =========================
        # RESPONSE
        # =========================

        return [
            NotificationResponse(

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