from modules.notifications.domain.exceptions import (
    NotificationNotFound,
)
from modules.auth.domain.exceptions import Unauthorized

from modules.notifications.application.dtos.delete_notification_dto import (
    DeleteNotificationDTO,
)
from modules.notifications.application.results.delete_notification_result import (
    DeleteNotificationResult,
)


class DeleteNotificationUseCase:
    """
    Supprime une notification après vérification de son existence
    et de son appartenance à l'utilisateur connecté, puis met à jour
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
        dto: DeleteNotificationDTO,
    ) -> DeleteNotificationResult:

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
            # DELETE
            # =========================

            self.repository.delete(
                notification.id
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

        return DeleteNotificationResult(
            id=notification.id,
            success=True,
            message="Notification supprimée",
        )