from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    Date,
    ForeignKey,
    Boolean,
    Enum as SqlEnum
)

from sqlalchemy.orm import relationship

from core.database.session import Base

from modules.applications.domain.enums import ApplicationStatus

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
    quote_id = Column(
        String,
        ForeignKey(
            "quotes.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        unique=True,
        index=True
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

    birth_date = Column(Date, nullable=True)

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

    previous_status = Column(
    SqlEnum(ApplicationStatus),
    nullable=True
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

    discount = Column(
    Float,
    nullable=True,
    default=0
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

    payment = relationship(
    "PaymentModel",
    back_populates="application",
    cascade="all, delete-orphan"
)
    
    financing_contract = relationship(
    "FinancingContractModel",
    back_populates="application",
    uselist=False
)
    reservation = relationship(
    "ReservationModel",
    back_populates="application",
    uselist=False
)
    tickets = relationship("SupportTicketModel", back_populates="application")

    quote = relationship(
        "QuoteModel",
        back_populates="application",
        uselist=False
    )