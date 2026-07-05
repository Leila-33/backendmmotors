from uuid import uuid4
from datetime import datetime, timezone


from modules.notifications.domain.entities.notification import Notification
from modules.core.enums import NotificationStatus, NotificationType
from modules.core.exceptions import InvalidNotificationType


class NotificationService:

    def __init__(
        self,
        notification_repo,
        email_service,
        websocket_manager=None
    ):
        self.notification_repo = notification_repo
        self.email_service = email_service
        self.websocket_manager = websocket_manager

    async def send(
        self,
        user_id: str,
        email: str,
        title: str,
        message: str,
        notif_type: NotificationType | str,
        application_id: str | None = None,
        test_drive_id: str | None = None,
    ):

        # =========================
        # NORMALISATION TYPE SAFE
        # =========================
        if isinstance(notif_type, str):
            try:
                notif_type = NotificationType(notif_type)
            except ValueError:
                raise InvalidNotificationType(notif_type)

        # =========================
        # CREATE NOTIFICATION
        # =========================
        notification = Notification(
            id=str(uuid4()),
            user_id=user_id,
            application_id=application_id,
            test_drive_id=test_drive_id,
            title=title,
            message=message,
            type=notif_type,
            status=NotificationStatus.UNREAD,
            created_at=datetime.now(timezone.utc)
        )
        print(notification.id)
        # =========================
        # SAVE DB
        # =========================
        self.notification_repo.save(notification)
        self.notification_repo.commit()

        # =========================
        # EMAIL (SAFE)
        # =========================
        try:
            self.email_service.send(
                to=email,
                subject=title,
                body=message
            )
        except Exception:
            pass

        # =========================
        # REALTIME PUSH (FIX IMPORTANT)
        # =========================
        if self.websocket_manager:
            await self.websocket_manager.send(
                user_id,
                {
                    "id": notification.id,
                    "title": title,
                    "message": message,
                    "type": notif_type.value,
                    "application_id": application_id,
                    "test_drive_id": test_drive_id,
                    "created_at": notification.created_at.isoformat(),
                }
            )

        return notification