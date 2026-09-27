from uuid import uuid4
from datetime import datetime, timezone


from modules.notifications.domain.entities.notification import Notification
from modules.notifications.domain.enums import NotificationStatus, NotificationType, NotificationEntityType
from modules.notifications.domain.exceptions import (
    InvalidNotificationType,
    InvalidNotificationEntityType
)


class NotificationService:
    """
    Crée et envoie des notifications aux utilisateurs.

    Une notification peut être enregistrée en base, envoyée par e-mail
    et transmise en temps réel via WebSocket.
    """
    def __init__(
        self,
        notification_repo,
        email_service,
        websocket_manager=None,
    ):
        self.notification_repo = notification_repo
        self.email_service = email_service
        self.websocket_manager = websocket_manager

    # ==========================================================
    # SEND NOTIFICATION
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

        # ======================================================
        # NORMALISE NOTIFICATION TYPE
        # ======================================================

        if isinstance(notif_type, str):

            try:
                notif_type = NotificationType(
                    notif_type
                )

            except ValueError:
                raise InvalidNotificationType(
                    notif_type
                )

        # ======================================================
        # NORMALISE ENTITY TYPE
        # ======================================================

        if isinstance(entity_type, str):

            try:
                entity_type = NotificationEntityType(
                    entity_type
                )

            except ValueError:
                raise InvalidNotificationEntityType(
                    entity_type
                )

        # ======================================================
        # CREATE NOTIFICATION
        # ======================================================

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

        # ======================================================
        # SAVE
        # ======================================================

        self.notification_repo.save(
            notification
        )

        # ======================================================
        # EMAIL
        # ======================================================

        if email:

            self.email_service.send(
                to=email,
                subject=title,
                body=message,
            )

        # ======================================================
        # WEBSOCKET
        # ======================================================

        if self.websocket_manager:

            await self.websocket_manager.send(
                user_id,
                {
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

                    "created_at": (
                        notification.created_at.isoformat()
                    ),
                },
            )

        return notification

    # ==========================================================
    # SEND UPDATE
    # ==========================================================

    async def send_update(
        self,
        user_id: str,
        payload: dict,
    ) -> None:

        # ======================================================
        # WEBSOCKET NON CONFIGURÉ
        # ======================================================

        if self.websocket_manager is None:
            return

        # ======================================================
        # SEND WEBSOCKET UPDATE
        # ======================================================

        await self.websocket_manager.send(
            user_id,
            payload,
        )