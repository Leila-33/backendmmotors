from sqlalchemy import Column, String, Integer, Boolean, Float, Text, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from infrastructure.db.session import Base
from modules.core.enums import WarrantyPlanType


class WarrantyPlanModel(Base):
    __tablename__ = "warranty_plans"
    __table_args__ = (
        UniqueConstraint(
            "plan_type",
            "duration_months",
            name="uq_warranty_plan_type_duration"
        ),
    )
    id = Column(String, primary_key=True)

    # infos générales
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    plan_type = Column(
        Enum(WarrantyPlanType),
        default=WarrantyPlanType.STANDARD,
        nullable=False
    )

    # durée & limites
    duration_months = Column(Integer, nullable=False)
    mileage_limit = Column(Integer, nullable=True)

    # couverture mécanique
    covers_engine = Column(Boolean, default=True)
    covers_transmission = Column(Boolean, default=True)
    covers_electronics = Column(Boolean, default=False)
    covers_assistance = Column(Boolean, default=False)
    covers_wear_parts = Column(Boolean, default=False)

    # conditions financières
    deductible = Column(Float, default=0.0)
    price = Column(Float, nullable=False)

    # statut
    active = Column(Boolean, default=True)

    # relation inverse
    warranties = relationship(
        "VehicleWarrantyModel",
        back_populates="warranty_plan"
    )