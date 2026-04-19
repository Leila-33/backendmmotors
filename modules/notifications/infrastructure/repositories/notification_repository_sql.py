from sqlalchemy.orm import Session
from typing import List

from infrastructure.db.session import SessionLocal

from modules.notifications.domain.entities.notification import Notification, NotificationStatus
from modules.notifications.infrastructure.db.models.notification_model import NotificationModel
from modules.notifications.domain.repositories.notification_repository import NotificationRepository


class NotificationRepositorySQL(NotificationRepository):

    # =====================
    # SAVE
    # =====================
    def save(self, notification: Notification):

        db: Session = SessionLocal()

        model = NotificationModel(
            id=notification.id,
            user_id=notification.user_id,
            application_id=notification.application_id,
            title=notification.title,
            message=notification.message,
            type=notification.type.value,
            status=notification.status.value,
            is_read=notification.is_read,
            created_at=notification.created_at
        )

        db.add(model)
        db.commit()

    # =====================
    # GET BY USER
    # =====================
    def get_by_user(self, user_id: str) -> List[Notification]:

        db: Session = SessionLocal()

        results = db.query(NotificationModel)\
            .filter(NotificationModel.user_id == user_id)\
            .order_by(NotificationModel.created_at.desc())\
            .all()

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

    # =====================
    # MARK AS READ
    # =====================
    def mark_as_read(self, notification_id: str):

        db: Session = SessionLocal()

        notification = db.query(NotificationModel)\
            .filter(NotificationModel.id == notification_id)\
            .first()

        if notification:
            notification.is_read = True
            notification.status = NotificationStatus.READ.value
            db.commit()