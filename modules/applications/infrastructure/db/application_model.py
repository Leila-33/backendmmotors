# =========================================================
# SQLALCHEMY MODEL
# modules/applications/infrastructure/models/application_model.py
# =========================================================

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Enum as SqlEnum
)

from sqlalchemy.orm import relationship

from infrastructure.db.session import Base

from modules.core.enums import (
    ApplicationStatus
)
from modules.applications.infrastructure.db.application_financing_model import ApplicationFinancingModel
from modules.applications.infrastructure.db.application_trade_in_model import ApplicationTradeInModel


class ApplicationModel(Base):

    __tablename__ = "applications"

    # =====================================================
    # IDENTIFIERS
    # =====================================================
    id = Column(String, primary_key=True)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    vehicle_id = Column(
        String,
        ForeignKey("vehicles.id"),
        nullable=False
    )

    # =====================================================
    # SNAPSHOT USER
    # nullable=True IMPORTANT
    # because draft can be incomplete
    # =====================================================
    first_name = Column(String, nullable=True)

    last_name = Column(String, nullable=True)

    email = Column(String, nullable=True)

    phone = Column(String, nullable=True)

    address = Column(String, nullable=True)

    birth_date = Column(DateTime, nullable=True)

    # =====================================================
    # FINANCIAL INFO
    # =====================================================
    monthly_income = Column(
        Float,
        nullable=True
    )

    monthly_expenses = Column(
        Float,
        nullable=True
    )

    employment_status = Column(
        String,
        nullable=True
    )

    # =====================================================
    # STATUS
    # =====================================================
    status = Column(
        SqlEnum(ApplicationStatus),
        nullable=False,
        default=ApplicationStatus.DRAFT
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    submitted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
    # =====================================================
    # ARCHIVE
    # =====================================================
    is_archived = Column(
        Boolean,
        nullable=False,
        default=False
    )

    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True)
    # =====================================================
    # RELATIONS
    # =====================================================

    # USER
    user = relationship(
        "UserModel",
        back_populates="applications"
    )

    # VEHICLE
    vehicle = relationship(
        "VehicleModel",
        back_populates="applications"
    )

    # DOCUMENTS
    documents = relationship(
        "DocumentModel",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    # EVENTS
    events = relationship(
        "EventModel",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    # NOTIFICATIONS
    notifications = relationship(
        "NotificationModel",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    # OPTIONS
    options = relationship(
        "ApplicationOptionModel",
        back_populates="application",
        cascade="all, delete-orphan"
    )

    # FINANCING (1-1)
    financing = relationship(
        "ApplicationFinancingModel",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan"
    )

    # TRADE-IN (1-1)
    trade_in = relationship(
        "ApplicationTradeInModel",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan"
    )