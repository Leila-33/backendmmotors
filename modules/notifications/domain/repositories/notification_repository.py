from abc import ABC, abstractmethod
from modules.notifications.domain.entities.notification import Notification


class NotificationRepository(ABC):

    @abstractmethod
    def save(self, notification: Notification):
        pass

    @abstractmethod
    def get_by_user(self, user_id: str):
        pass

    @abstractmethod
    def mark_as_read(self, notification_id: str):
        pass