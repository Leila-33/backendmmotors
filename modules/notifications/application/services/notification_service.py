from uuid import uuid4
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)

from modules.notifications.domain.entities.notification import Notification
from modules.notifications.domain.enums import NotificationStatus, NotificationType, NotificationEntityType
from modules.notifications.domain.exceptions import (
    InvalidNotificationType,
    InvalidNotificationEntityType
)



class NotificationService:
    """
    Crée et envoie les notifications utilisateur.

    Les notifications persistantes sont enregistrées en base.
    Les mises à jour temps réel sont publiées dans Redis afin que
    le listener les relaie aux connexions WebSocket locales.
    """

    def __init__(
        self,
        notification_repo,
        email_service,
        redis_conn=None,
    ):
        self.notification_repo = notification_repo
        self.email_service = email_service
        self.redis_conn = redis_conn

    # ==========================================================
    # SEND PERSISTENT NOTIFICATION
    # ==========================================================

    async def send(
        self,
        user_id: str,
        title: str,
        message: str,
        notif_type: NotificationType | str,
        email: str | None = None,
        entity_type: NotificationEntityType | str | None = None,
        entity_id: str | None = None,
    ) -> Notification:

        if isinstance(notif_type, str):
            try:
                notif_type = NotificationType(notif_type)
            except ValueError as exc:
                raise InvalidNotificationType(notif_type) from exc

        if isinstance(entity_type, str):
            try:
                entity_type = NotificationEntityType(entity_type)
            except ValueError as exc:
                raise InvalidNotificationEntityType(entity_type) from exc

        notification = Notification(
            id=str(uuid4()),
            user_id=user_id,
            title=title,
            message=message,
            type=notif_type,
            status=NotificationStatus.UNREAD,
            created_at=datetime.now(timezone.utc),
            entity_type=entity_type,
            entity_id=entity_id,
        )

        self.notification_repo.save(notification)

        if email:
            self.email_service.send(
                to=email,
                subject=title,
                body=message,
            )

        # Publier la notification persistante dans Redis.
        await self.send_update(
            user_id=user_id,
            payload={
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type.value,
                "status": notification.status.value,
                "entity_type": (
                    notification.entity_type.value
                    if notification.entity_type
                    else None
                ),
                "entity_id": notification.entity_id,
                "created_at": notification.created_at.isoformat(),
            },
        )

        return notification

    # ==========================================================
    # SEND REAL-TIME UPDATE THROUGH REDIS
    # ==========================================================

    async def send_update(
        self,
        user_id: str,
        payload: dict,
    ) -> None:

        if self.redis_conn is None:
            logger.warning(
                "Redis non configuré : notification non publiée "
                "pour user_id=%s",
                user_id,
            )
            return

        event = {
            "user_id": str(user_id),
            "message": payload,
        }

        try:
            result = self.redis_conn.publish(
                "user_notifications",
                json.dumps(event),
            )

            # Compatible avec un client Redis synchrone ou asynchrone.
            if hasattr(result, "__await__"):
                await result

        except Exception:
            logger.exception(
                "Échec de publication Redis pour user_id=%s",
                user_id,
            )
            raise