from abc import ABC, abstractmethod
from modules.notifications.domain.entities.notification import Notification
from typing import List, Optional



class NotificationRepository(ABC):

    @abstractmethod
    def save(self, notification: Notification):
        pass

    @abstractmethod
    def get_by_user(self, user_id: str):
        pass
    @abstractmethod
    def delete_by_application(self, application_id: str):
        pass


    # =========================
    # GET BY ID
    # =========================
    @abstractmethod
    def get_by_id(self, notification_id: str) -> Optional[Notification]:
        pass

    # =========================
    # GET BY USER
    # =========================
    @abstractmethod
    def get_by_user_id(self, user_id: str) -> List[Notification]:
        pass

    # =========================
    # UPDATE
    # =========================
    @abstractmethod
    def update(self, notification: Notification) -> Notification:
        pass

    # =========================
    # DELETE (OPTIONAL)
    # =========================
    @abstractmethod
    def delete(self, notification_id: str) -> None:
        pass

    # =========================
    # COUNT UNREAD (UX BADGE)
    # =========================
    @abstractmethod
    def count_unread(self, user_id: str) -> int:
        pass


   
    @abstractmethod
    def commit(self) -> None:
        pass