from modules.core.exceptions import NotificationNotFound, Unauthorized

class DeleteNotificationUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, notification_id: str, user_id: str):

        # =========================
        # GET NOTIFICATION
        # =========================
        notification = self.repository.get_by_id(notification_id)

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
        self.repository.delete(notification_id)

        return {
            "success": True,
            "message": "Notification supprimée"
        }