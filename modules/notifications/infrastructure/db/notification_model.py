from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship

from core.database.session import Base
from modules.notifications.domain.enums import (
    NotificationType,
    NotificationStatus,
    NotificationEntityType
)

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class NotificationModel(Base):

    __tablename__ = "notifications"


    id = Column(
        String,
        primary_key=True,
    )


    user_id = Column(
        String,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True,
    )


    # =====================
    # CONTEXT
    # =====================


    entity_type = Column(
        Enum(NotificationEntityType),
        nullable=True,
        index=True,
    )


    entity_id = Column(
        String,
        nullable=True,
        index=True,
    )


    # =====================
    # CONTENT
    # =====================

    title = Column(
        String,
        nullable=False,
    )


    message = Column(
        String,
        nullable=False,
    )


    # =====================
    # ENUMS
    # =====================

    type = Column(
        Enum(
            NotificationType,
            name="notification_type",
        ),
        nullable=False,
    )


    status = Column(
        Enum(
            NotificationStatus,
            name="notification_status",
        ),
        nullable=False,
        default=NotificationStatus.UNREAD,
    )


    # =====================
    # TIMESTAMP
    # =====================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =====================
    # RELATIONS
    # =====================

    user = relationship(
        "UserModel",
        back_populates="notifications",
    )