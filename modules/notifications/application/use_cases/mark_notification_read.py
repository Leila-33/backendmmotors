from modules.auth.domain.exceptions import Unauthorized
from modules.notifications.domain.exceptions import (
    NotificationNotFound,
)

from modules.notifications.application.dtos.mark_notification_read_dto import (
    MarkNotificationReadDTO,
)

from modules.notifications.application.results.mark_notification_read_result import (
    MarkNotificationReadResult,
)


class MarkNotificationReadUseCase:
    """
    Marque une notification comme lue après vérification
    de son appartenance à l'utilisateur connecté, puis met à jour
    le compteur de notifications non lues en temps réel.
    """
    def __init__(
        self,
        repository,
        notification_service,
        unit_of_work,
    ):
        self.repository = repository
        self.notification_service = notification_service
        self.unit_of_work = unit_of_work

    async def execute(
        self,
        dto: MarkNotificationReadDTO,
    ) -> MarkNotificationReadResult:

        try:

            # =========================
            # GET NOTIFICATION
            # =========================

            notification = (
                self.repository
                .get_by_id(
                    dto.notification_id
                )
            )

            if notification is None:
                raise NotificationNotFound()

            # =========================
            # SECURITY CHECK
            # =========================

            if notification.user_id != dto.user_id:
                raise Unauthorized()

            # =========================
            # DOMAIN ACTION
            # =========================

            notification.mark_as_read()

            # =========================
            # UPDATE
            # =========================

            self.repository.update(
                notification
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            

            count = (
                self.repository
                .count_unread(
                    dto.user_id
                )
            )

            await self.notification_service.send_update(
                user_id=dto.user_id,
                payload={
                    "type": "UNREAD_NOTIFICATIONS_UPDATED",
                    "count": count,
                },
            )

        except Exception:

            self.unit_of_work.rollback()
            raise

        return MarkNotificationReadResult(
            success=True,
            message="Notification marquée comme lue",
        )