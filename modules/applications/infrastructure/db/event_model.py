from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from core.database.session import Base


class EventModel(Base):

    __tablename__ = "events"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    # =====================================================
    # CONTENT
    # =====================================================

    type = Column(
        String(100),
        nullable=False,
        index=True,
    )

    message = Column(
        String,
        nullable=False,
    )

    event_metadata = Column(
        JSON,
        nullable=True,
    )

    # =====================================================
    # TIMESTAMP
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # =====================================================
    # CONTEXT / FOREIGN KEYS
    # =====================================================

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    vehicle_id = Column(
        String,
        ForeignKey("vehicles.id"),
        nullable=True,
        index=True,
    )

    quote_id = Column(
        String,
        ForeignKey("quotes.id"),
        nullable=True,
        index=True,
    )

    application_id = Column(
        String,
        ForeignKey("applications.id"),
        nullable=True,
        index=True,
    )

    test_drive_id = Column(
        String,
        ForeignKey("test_drives.id"),
        nullable=True,
        index=True,
    )

    lead_id = Column(
        String,
        ForeignKey("leads.id"),
        nullable=True,
        index=True,
    )

    # =====================================================
    # RELATIONS
    # =====================================================

    user = relationship(
        "UserModel",
        back_populates="events",
    )

    vehicle = relationship(
        "VehicleModel",
        back_populates="events",
    )

    quote = relationship(
        "QuoteModel",
        back_populates="events",
    )

    application = relationship(
        "ApplicationModel",
        back_populates="events",
    )

    test_drive = relationship(
        "TestDriveModel",
        back_populates="events",
    )

    lead = relationship(
        "LeadModel",
        back_populates="events",
    )