from sqlalchemy import Column, Date, DateTime, ForeignKey, Enum, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.database.session import Base
from modules.reservations.domain.enums import ReservationStatus

class ReservationModel(Base):
    __tablename__ = "reservations"
    UniqueConstraint("application_id")
    id = Column(String, primary_key=True, index=True)

    vehicle_id = Column(
        String,
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    application_id = Column(
        String,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    status = Column(
        Enum(ReservationStatus),
        nullable=False,
        default=ReservationStatus.ACTIVE,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # =========================
    # RELATIONS
    # =========================
    vehicle = relationship(
        "VehicleModel",
        back_populates="reservations"
    )

    application = relationship(
        "ApplicationModel",
        back_populates="reservation"
    )