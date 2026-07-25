from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from core.database.session import Base
class VehicleWarrantyModel(Base):
    __tablename__ = "vehicle_warranties"

    # =========================
    # PRIMARY KEY
    # =========================
    id = Column(String, primary_key=True, index=True)

    # =========================
    # RELATIONS
    # =========================
    vehicle_id = Column(
        String,
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    warranty_plan_id = Column(
        String,
        ForeignKey("warranty_plans.id"),
        nullable=False,
        index=True
    )

    # =========================
    # DATES
    # =========================
    start_date = Column(
        DateTime,
        nullable=True   # 🔥 important (création ≠ activation)
    )

    end_date = Column(
        DateTime,
        nullable=True   # 🔥 idem
    )

    # =========================
    # STATUS
    # =========================
    is_active = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )

    # =========================
    # USAGE
    # =========================
    current_mileage = Column(
        Integer,
        nullable=False,
        default=0
    )

    max_mileage = Column(
        Integer,
        nullable=True
    )

    # =========================
    # RELATIONS ORM
    # =========================
    vehicle = relationship(
        "VehicleModel",
        back_populates="warranty",
        uselist=False
    )

    warranty_plan = relationship(
        "WarrantyPlanModel",
        back_populates="warranties"
    )