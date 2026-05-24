from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Enum, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from infrastructure.db.session import Base
from modules.core.enums import ReservationStatus
from modules.auth.infrastructure.db.user_model import UserModel

class ReservationModel(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(
        String,
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    status = Column(
        Enum(ReservationStatus),
        nullable=False,
        default=ReservationStatus.ACTIVE
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    # =========================
    # RELATIONS
    # =========================
    vehicle = relationship(
        "VehicleModel",
        back_populates="reservations"
    )

    user = relationship(
        "UserModel",
        back_populates="reservations"
    )