from sqlalchemy.orm import Session
from modules.notifications.infrastructure.mappers.notification_mapper import NotificationMapper
from modules.notifications.domain.entities.notification import Notification
from modules.notifications.infrastructure.db.notification_model import NotificationModel
from modules.notifications.domain.repositories.notification_repository import NotificationRepository
from modules.notifications.domain.enums import NotificationStatus



class NotificationRepositorySQL(
    NotificationRepository
):

    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    # =====================
    # SAVE
    # =====================

    def save(
        self,
        notification: Notification,
    ):

        model = (
            NotificationMapper
            .to_model(notification)
        )

        self.db.add(model)

        self.db.flush()


    # =====================
    # GET BY ID
    # =====================

    def get_by_id(
        self,
        notification_id: str,
    ) -> Notification | None:

        model = (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.id == notification_id
            )
            .first()
        )

        if model is None:
            return None

        return (
            NotificationMapper
            .to_domain(model)
        )


    # =====================
    # GET BY USER
    # =====================

    def get_by_user(
        self,
        user_id: str,
    ) -> list[Notification]:

        models = (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.user_id == user_id
            )
            .order_by(
                NotificationModel.created_at.desc()
            )
            .all()
        )

        return [
            NotificationMapper.to_domain(model)
            for model in models
        ]


    # =====================
    # UPDATE
    # =====================

    def update(
        self,
        notification: Notification,
    ):

        model = (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.id == notification.id
            )
            .first()
        )

        if model is None:
            return

        NotificationMapper.update_model(
            model,
            notification,
        )

        self.db.flush()


    # =====================
    # COUNT UNREAD
    # =====================

    def count_unread(
        self,
        user_id: str,
    ) -> int:

        return (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.user_id == user_id,
                NotificationModel.status == NotificationStatus.UNREAD,
            )
            .count()
        )


    # =====================
    # DELETE
    # =====================

    def delete(
        self,
        notification_id: str,
    ):

        (
            self.db.query(NotificationModel)
            .filter(
                NotificationModel.id == notification_id
            )
            .delete()
        )


    # =====================
    # DELETE BY APPLICATION
    # =====================

    def delete_by_entity(
    self,
    entity_type: str,
    entity_id: str,
) -> None:


        self.db.query(NotificationModel)\
            .filter(
                NotificationModel.entity_type == entity_type,
                NotificationModel.entity_id == entity_id,
            )\
            .delete(
                synchronize_session=False
            )

    