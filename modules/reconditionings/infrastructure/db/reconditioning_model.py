from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from core.database.session import Base
from modules.reconditionings.domain.enums import ReconditioningStatus


class ReconditioningModel(Base):
    __tablename__ = "reconditioning"

    # =========================
    # PRIMARY KEY
    # =========================
    id = Column(String, primary_key=True)

    # =========================
    # RELATION VEHICLE
    # =========================
    vehicle_id = Column(
        String,
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    vehicle = relationship(
        "VehicleModel",
        back_populates="reconditioning"
    )

    # =========================
    # STATUS
    # =========================
    status = Column(
        Enum(ReconditioningStatus),
        nullable=False,
        default=ReconditioningStatus.PENDING
    )

    # =========================
    # BUSINESS FIELDS
    # =========================
    cost = Column(Float, default=0.0)
    duration_days = Column(Integer, default=0)

    # JSON-like data
    tasks = Column(JSONB, default=list, nullable=False)

    # =========================
    # TIMESTAMPS
    # =========================
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)