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

    def __init__(
        self,
        repository,
        unit_of_work,
    ):
        self.repository = repository
        self.unit_of_work = unit_of_work

    def execute(
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

        except Exception:

            self.unit_of_work.rollback()
            raise

        return MarkNotificationReadResult(
            success=True,
            message="Notification marquée comme lue",
        )