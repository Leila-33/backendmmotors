from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import relationship

from infrastructure.db.session import Base
from modules.core.enums import NotificationType, NotificationStatus

class NotificationModel(Base):

    __tablename__ = "notifications"

    id = Column(String, primary_key=True)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =====================
    # CONTEXT RELATIONS
    # =====================

    application_id = Column(
        String,
        ForeignKey("applications.id"),
        nullable=True,
        index=True
    )

    test_drive_id = Column(
        String,
        ForeignKey("test_drives.id"),
        nullable=True,
        index=True
    )

    document_id = Column(
        String,
        ForeignKey("documents.id"),
        nullable=True,
        index=True
    )

    # =====================
    # CONTENT
    # =====================
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)

    # =====================
    # ENUMS
    # =====================
    type = Column(
        Enum(
            NotificationType,
            name="notification_type",
        ),
        nullable=False
    )

    status = Column(
        Enum(
            NotificationStatus,
            name="notification_status",
        ),
        nullable=False
    )

    # =====================
    # TIMESTAMP
    # =====================
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # =====================
    # RELATIONS
    # =====================
    user = relationship("UserModel", back_populates="notifications")

    application = relationship("ApplicationModel", back_populates="notifications")

    test_drive = relationship("TestDriveModel", back_populates="notifications")

    document = relationship("DocumentModel", back_populates="notifications")
    