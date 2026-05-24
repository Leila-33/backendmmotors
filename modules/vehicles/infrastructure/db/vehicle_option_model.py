import enum
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from infrastructure.db.session import Base
from sqlalchemy import UniqueConstraint

from modules.vehicles.infrastructure.db.vehicle_model import VehicleModel
from modules.core.enums import VehicleOptionType



class VehicleOptionModel(Base):
    __tablename__ = "vehicle_options"

    __table_args__ = (
        UniqueConstraint("vehicle_id", "option_id", name="uq_vehicle_option"),
    )

    id = Column(String, primary_key=True)

    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False)
    option_id = Column(String, ForeignKey("options.id"), nullable=False)

    type = Column(SQLEnum(VehicleOptionType), nullable=False)

    # relations
    vehicle = relationship("VehicleModel", back_populates="options")
    option = relationship("OptionModel", back_populates="vehicle_links")