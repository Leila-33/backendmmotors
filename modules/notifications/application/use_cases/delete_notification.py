from modules.notifications.domain.exceptions import NotificationNotFound
from modules.auth.domain.exceptions import Unauthorized
from modules.notifications.api.schemas import DeleteNotificationResponse

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
        notification_id: str,
        user_id: str,
    ):

        try:

            # =========================
            # GET NOTIFICATION
            # =========================

            notification = (
                self.repository
                .get_by_id(
                    notification_id
                )
            )


            if not notification:
                raise NotificationNotFound()



            # =========================
            # SECURITY CHECK
            # =========================

            if notification.user_id != user_id:
                raise Unauthorized()



            # =========================
            # DELETE
            # =========================

            self.repository.delete(
                notification_id
            )


            self.unit_of_work.commit()



        except Exception:

            self.unit_of_work.rollback()

            raise



        return DeleteNotificationResponse(

            id=notification.id,

            success=True,

            message=(
                "Notification supprimée"
            )

        )