from datetime import datetime, timezone
from modules.payments.domain.enums import SubscriptionStatus

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SqlEnum
)

from sqlalchemy.orm import relationship

from core.database.session import Base


class FinancingContractModel(Base):

    __tablename__ = "financing_contracts"

    # =========================
    # PRIMARY KEY
    # =========================
    id = Column(
        String,
        primary_key=True
    )

    # =========================
    # APPLICATION
    # =========================
    application_id = Column(
        String,
        ForeignKey("applications.id"),
        nullable=False,
        unique=True
    )

    # =========================
    # FINANCING
    # =========================
    financed_amount = Column(
        Float,
        nullable=False
    )

    monthly_payment = Column(
        Float,
        nullable=False
    )

    duration_months = Column(
        Integer,
        nullable=False
    )

    remaining_balance = Column(
        Float,
        nullable=False
    )

    # =========================
    # STRIPE
    # =========================
    stripe_customer_id = Column(
        String,
        nullable=True
    )

    stripe_subscription_id = Column(
        String,
        nullable=True,
        unique=True
    )

    subscription_status = Column(
    SqlEnum(SubscriptionStatus),
    nullable=True,
    default=SubscriptionStatus.ACTIVE
)

    # =========================
    # TIMESTAMPS
    # =========================
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # =========================
    # RELATIONSHIPS
    # =========================
    application = relationship(
        "ApplicationModel",
        back_populates="financing_contract"
    )

    installments = relationship(
    "InstallmentPaymentModel",
    back_populates="financing_contract",
    cascade="all, delete-orphan"
)