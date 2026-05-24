from sqlalchemy import Column, String, Float, Integer, Boolean, Text, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from infrastructure.db.session import Base
from modules.core.enums import (
    VehicleType,
    EngineType,
    VehicleCondition
)
from modules.reservations.infrastructure.db.reservation_model import ReservationModel

class VehicleModel(Base):
    __tablename__ = "vehicles"

    # =========================
    # PRIMARY KEY
    # =========================
    id = Column(String, primary_key=True, index=True)

    # =========================
    # BASIC INFO
    # =========================
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)

    price = Column(Float, nullable=False)

    type = Column(
        SqlEnum(VehicleType, name="vehicle_type"),
        nullable=False
    )

    mileage = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    # =========================
    # DETAILS
    # =========================
    description = Column(Text, nullable=True)

    engine_type = Column(
        SqlEnum(EngineType, name="engine_type"),
        nullable=True
    )

    equipments = Column(
        ARRAY(String),
        nullable=False,
        default=list   # ✔ mieux que []
    )

    condition = Column(
        SqlEnum(VehicleCondition, name="vehicle_condition"),
        nullable=False,
        default=VehicleCondition.USED
    )

    # =========================
    # 🚗 NEW FIELD
    # =========================
    license_plate = Column(
        String,
        nullable=True,
        index=True,
        unique=True  # ✔ important si immatriculation unique
    )

    # =========================
    # STATUS
    # =========================
    is_available = Column(Boolean, default=True, nullable=False)

    # =========================
    # MEDIA
    # =========================
    images = Column(
        ARRAY(String),
        nullable=False,
        default=list  # ✔ correction importante
    )

    # =========================
    # RELATIONS
    # =========================
    options = relationship(
        "VehicleOptionModel",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    applications = relationship(
        "ApplicationModel",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    reservations = relationship(
        "ReservationModel",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    test_drives = relationship(
    "TestDriveModel",
    back_populates="vehicle"
)
    favorites = relationship(
        "FavoriteModel",
        back_populates="vehicle",
        cascade="all, delete-orphan"
    )