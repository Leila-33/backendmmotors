from sqlalchemy import Column, String, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from infrastructure.db.session import Base
from modules.core.enums import OptionType, BillingType

from sqlalchemy import (
    Column,
    String,
    Float,
    Boolean,
    Enum
)




class OptionModel(Base):

    __tablename__ = "options"

    id = Column(String, primary_key=True)

    name = Column(String, nullable=False)

    # =========================
    # OPTION TYPE
    # =========================
    type = Column(
        Enum(OptionType),
        nullable=False
    )

    # =========================
    # PRICE
    # =========================
    price = Column(
        Float,
        nullable=True
    )

    # =========================
    # BILLING TYPE
    # =========================
    billing_type = Column(
        Enum(BillingType),
        nullable=False,
        default=BillingType.fixed
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

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