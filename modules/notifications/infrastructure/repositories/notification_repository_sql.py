from sqlalchemy.orm import Session
from typing import List


from modules.notifications.domain.entities.notification import Notification
from modules.notifications.infrastructure.db.notification_model import NotificationModel
from modules.notifications.domain.repositories.notification_repository import NotificationRepository
from modules.core.enums import NotificationStatus
from sqlalchemy import delete



class NotificationRepositorySQL(NotificationRepository):

    def __init__(self, db: Session):

        self.db = db

    # =====================
    # SAVE
    # =====================
    def save(self, notification: Notification):

        model = NotificationModel(
            id=notification.id,
            user_id=notification.user_id,
            application_id=notification.application_id,
            test_drive_id=notification.test_drive_id,
            title=notification.title,
            message=notification.message,
            type=notification.type.value,
            status=notification.status.value,
            created_at=notification.created_at
        )

        self.db.add(model)
        self.db.flush()

    # =====================
    # GET BY USER
    # =====================
    def get_by_user(self, user_id: str) -> List[Notification]:

        results = (
            self.db.query(NotificationModel)
            .filter(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .all()
        )

        return [
            Notification(
                id=n.id,
                user_id=n.user_id,
                application_id=n.application_id,
                title=n.title,
                message=n.message,
                type=n.type,
                status=n.status,
                is_read=n.is_read,
                created_at=n.created_at
            )
            for n in results
        ]


    def delete_by_application(self, application_id: str):

            self.db.query(NotificationModel)\
                .filter(NotificationModel.application_id == application_id)\
                .delete()

            self.db.commit()





    def get_by_user_id(self, user_id: str):

        return (
            self.db.query(NotificationModel)
            .filter(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .all()
        )

    def get_by_id(self, notification_id: str):

        return (
            self.db.query(NotificationModel)
            .filter(NotificationModel.id == notification_id)
            .first()
        )

    def update(self, notification):

        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)

    def count_unread(self, user_id: str):

        return (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.user_id == user_id,
                NotificationModel.status == NotificationStatus.UNREAD
            )
            .count()
        )

    def delete(self, notification_id: str) -> None:

        self.db.query(NotificationModel)\
            .filter(NotificationModel.id == notification_id)\
            .delete()

        self.db.commit()

    
    def commit(self):
        self.db.commit()