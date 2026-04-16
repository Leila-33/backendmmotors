from sqlalchemy import Column, String, Float, Integer, Boolean, Enum as SqlEnum, Text
from sqlalchemy.dialects.postgresql import ARRAY

from infrastructure.db.session import Base
from modules.vehicles.domain.entities.vehicle import VehicleType, EngineType


class VehicleModel(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True)

    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)

    price = Column(Float, nullable=False)

    type = Column(SqlEnum(VehicleType), nullable=False)

    mileage = Column(Integer)
    year = Column(Integer)

    # 🔥 US2 fields
    description = Column(Text)
    engineType = Column(SqlEnum(EngineType))
    equipments = Column(ARRAY(String))   # liste équipements
    condition = Column(String)

    isAvailable = Column(Boolean, default=True)

    images = Column(ARRAY(String))  # URLs images