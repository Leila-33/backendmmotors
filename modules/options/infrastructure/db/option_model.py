from sqlalchemy import Column, String, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from infrastructure.db.session import Base
from modules.vehicles.infrastructure.db.vehicle_option_model import VehicleOptionModel
from modules.applications.infrastructure.db.application_option_model import ApplicationOptionModel
from modules.core.enums import OptionType

class OptionModel(Base):
    __tablename__ = "options"

    id = Column(String, primary_key=True)

    name = Column(String, nullable=False)

    # ✅ FIX: enum sécurisé en DB
    type = Column(Enum(OptionType), nullable=False)

    price = Column(Float, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    # =========================
    # RELATIONS
    # =========================

    vehicle_links = relationship(
        "VehicleOptionModel",
        back_populates="option",
        cascade="all, delete"
    )

    application_links = relationship(
        "ApplicationOptionModel",
        back_populates="option",
        cascade="all, delete"
    )