from abc import ABC, abstractmethod
from modules.notifications.domain.entities.notification import Notification
from typing import List, Optional



from abc import ABC, abstractmethod
from typing import Optional

from modules.notifications.domain.entities.notification import (
    Notification
)



class NotificationRepository(ABC):


    # =========================
    # SAVE
    # =========================

    @abstractmethod
    def save(
        self,
        notification: Notification
    ) -> None:
        pass



    # =========================
    # GET BY USER
    # =========================

    @abstractmethod
    def get_by_user(
        self,
        user_id: str
    ) -> list[Notification]:
        pass



    # =========================
    # DELETE BY APPLICATION
    # =========================

    @abstractmethod
    def delete_by_entity(
        self,
        entity_type: str,
        entity_id: str
    ) -> None:
        pass



    # =========================
    # GET BY ID
    # =========================

    @abstractmethod
    def get_by_id(
        self,
        notification_id: str
    ) -> Optional[Notification]:
        pass



    # =========================
    # UPDATE
    # =========================

    @abstractmethod
    def update(
        self,
        notification: Notification
    ) -> None:
        pass



    # =========================
    # DELETE
    # =========================

    @abstractmethod
    def delete(
        self,
        notification_id: str
    ) -> None:
        pass



    # =========================
    # COUNT UNREAD (BADGE)
    # =========================

    @abstractmethod
    def count_unread(
        self,
        user_id: str
    ) -> int:
        pass