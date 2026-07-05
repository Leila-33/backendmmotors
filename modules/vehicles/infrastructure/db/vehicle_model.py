from sqlalchemy import Column, String, Float, Integer, Boolean, Text, DateTime, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from infrastructure.db.session import Base
from modules.core.enums import (
    VehicleType,
    EngineType,
    VehicleCondition,
    VehicleStatus
)
from modules.applications.infrastructure.db.application_model import ApplicationModel

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
    final_check_at = Column(DateTime(timezone=True), nullable=True)
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
    is_available = Column(Boolean, default=False, nullable=False)
    
    published_at = Column(
    DateTime(timezone=True),
    nullable=True
)

    # =========================
    # MEDIA
    # =========================
    images = Column(
        ARRAY(String),
        nullable=False,
        default=list
    )
    status = Column(
        SqlEnum(VehicleStatus),
        nullable=False,
        default=VehicleStatus.AVAILABLE,

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
        ApplicationModel,
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

    warranty = relationship(
        "VehicleWarrantyModel",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        uselist=False
    )

    reconditioning = relationship(
    "ReconditioningModel",
    back_populates="vehicle",
    uselist=False,
    cascade="all, delete-orphan"
)
    inspections = relationship(
        "InspectionModel",
        back_populates="vehicle",
        cascade="all, delete-orphan"
    )