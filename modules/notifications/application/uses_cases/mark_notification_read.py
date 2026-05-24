from modules.core.exceptions import Unauthorized, NotificationNotFound 
from modules.core.enums import NotificationStatus

class MarkNotificationReadUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, notification_id: str, user_id: str):

        notification = self.repository.get_by_id(notification_id)

        if not notification:
            raise NotificationNotFound()

        if notification.user_id != user_id:
            raise Unauthorized()

        notification.status = NotificationStatus.READ

        self.repository.update(notification)

        return {"success": True}