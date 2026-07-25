
from core.database.session import Base
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from modules.applications.domain.enums import EventType

from datetime import datetime

class EventModel(Base):

    __tablename__ = "events"

    # =====================
    # PRIMARY KEY
    # =====================

    id = Column(
        String,
        primary_key=True,
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

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    # =====================
    # CONTENT
    # =====================

    type = Column(
    String(100),
    nullable=False
)

    message = Column(
        String,
        nullable=False
    )

    event_metadata = Column(
        JSON,
        nullable=True
    )

    # =====================
    # TIMESTAMP
    # =====================

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc)
    )

    # =====================
    # RELATIONS
    # =====================

    application = relationship(
        "ApplicationModel",
        back_populates="events"
    )

    user = relationship(
        "UserModel",
        back_populates="events"
    )

    test_drive = relationship(
        "TestDriveModel",
        back_populates="events"
    )