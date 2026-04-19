from datetime import datetime, timezone
import uuid

from modules.notifications.domain.entities.notification import Notification, NotificationStatus


class NotificationService:

    def __init__(self, notification_repo, email_service):
        self.notification_repo = notification_repo
        self.email_service = email_service

    def send(
        self,
        user_id: str,
        email: str,
        application_id: str,
        title: str,
        message: str,
        notif_type
    ):

        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            application_id=application_id,
            title=title,
            message=message,
            type=notif_type,
            status=NotificationStatus.UNREAD,
            is_read=False,
            created_at=datetime.now(timezone.utc)
        )

        # SAVE
        self.notification_repo.save(notification)

        # EMAIL
        self.email_service.send(
            to=email,
            subject=title,
            body=message
        )

        return notification