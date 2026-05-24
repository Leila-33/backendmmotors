from infrastructure.db.session import Base


from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from modules.core.enums import TestDriveStatus



class TestDriveModel(Base):

    __tablename__ = "test_drives"

    id = Column(String, primary_key=True)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    vehicle_id = Column(
        String,
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    appointment_date = Column(
        DateTime(timezone=True),
        nullable=False
    )

    status = Column(
        Enum(TestDriveStatus),
        nullable=False,
        default=TestDriveStatus.PENDING
    )

    comment = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    # =========================
    # RELATIONS (IMPORTANT)
    # =========================
    user = relationship(
        "UserModel",
        back_populates="test_drives"
    )
    vehicle = relationship("VehicleModel", back_populates="test_drives")

    notifications = relationship(
    "NotificationModel",
    back_populates="test_drive"
)
    events = relationship(
    "EventModel",
    back_populates="test_drive"
)