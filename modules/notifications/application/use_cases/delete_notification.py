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

    def __init__(
        self,
        repository,
        unit_of_work,
    ):
        self.repository = repository
        self.unit_of_work = unit_of_work

    def execute(
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

        except Exception:

            self.unit_of_work.rollback()
            raise

        return DeleteNotificationResult(
            id=notification.id,
            success=True,
            message="Notification supprimée",
        )