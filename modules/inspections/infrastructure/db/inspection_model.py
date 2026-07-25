from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB

from core.database.session import Base
from modules.inspections.domain.enums import InspectionStatus


class InspectionModel(Base):
    __tablename__ = "inspections"

    id = Column(String, primary_key=True)
    vehicle_id = Column(
            String,
            ForeignKey("vehicles.id", ondelete="CASCADE"),  # 🔥 OBLIGATOIRE
            nullable=False,
            index=True
        )
    status = Column(Enum(InspectionStatus), nullable=False)

    engine_score = Column(Integer, default=0)
    brakes_score = Column(Integer, default=0)
    tires_score = Column(Integer, default=0)
    electronics_score = Column(Integer, default=0)
    safety_score = Column(Integer, default=0)
    overall_score = Column(Integer, default=0)

    failures = Column(
    JSONB,
    nullable=True
)

    recommended_repairs = Column(
        JSONB,
        nullable=True
    )

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    vehicle = relationship("VehicleModel", back_populates="inspections")