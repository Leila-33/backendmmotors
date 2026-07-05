from sqlalchemy import Column, String, Integer, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from infrastructure.db.session import Base
from modules.core.enums import InspectionStatus


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

    failures = Column(Text, nullable=True)  # JSON string
    recommended_repairs = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    vehicle = relationship("VehicleModel", back_populates="inspections")