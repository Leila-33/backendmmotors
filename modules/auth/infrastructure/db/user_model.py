from sqlalchemy import Column, String, Boolean, Enum
from infrastructure.db.session import Base
from sqlalchemy.orm import relationship
from modules.notifications.infrastructure.db.notification_model import NotificationModel

from modules.core.enums import UserRole
from modules.applications.infrastructure.db.event_model import EventModel

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    role = Column(Enum(UserRole), default=UserRole.CLIENT, nullable=False)

    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    accepted_cgu = Column(Boolean, default=False, nullable=False)

    # =====================
    # RELATIONS
    # =====================

    events = relationship(
        "EventModel",
        back_populates="user"
    )

    applications = relationship(
        "ApplicationModel",
        back_populates="user"
    )

    notifications = relationship(
        "NotificationModel",
        back_populates="user"
    )

    reservations = relationship(
        "ReservationModel",
        back_populates="user",
        cascade="all, delete")
    
    test_drives = relationship(
    "TestDriveModel",
    back_populates="user",
    cascade="all, delete-orphan"
)
    favorites = relationship(
        "FavoriteModel",
        back_populates="user",
        cascade="all, delete-orphan"
    )