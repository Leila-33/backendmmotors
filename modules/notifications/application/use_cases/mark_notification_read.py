from modules.auth.domain.exceptions import Unauthorized 
from modules.notifications.domain.exceptions import NotificationNotFound 
from modules.notifications.api.schemas import MarkNotificationReadResponse


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
        notification_id: str,
        user_id: str,
    ):

        try:

            # =========================
            # GET NOTIFICATION
            # =========================

            notification = (
                self.repository
                .get_by_id(notification_id)
            )


            if not notification:
                raise NotificationNotFound()



            # =========================
            # SECURITY CHECK
            # =========================

            if notification.user_id != user_id:
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


            self.unit_of_work.commit()



        except Exception:

            self.unit_of_work.rollback()

            raise



        return MarkNotificationReadResponse(
            success=True,
            message="Notification marquée comme lue"
        )