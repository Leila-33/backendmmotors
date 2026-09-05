from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Float,
    Enum,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from core.database.session import Base

from modules.payments.domain.enums import PaymentStatus



class PaymentModel(Base):
    __tablename__ = "payments"

    # =========================
    # PRIMARY KEY
    # =========================
    id = Column(String, primary_key=True)

    # =========================
    # RELATIONS
    # =========================
    application_id = Column(
        String,
        ForeignKey("applications.id"),
        unique=True,
        nullable=False
    )

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    # =========================
    # STRIPE
    # =========================

    stripe_customer_id = Column(
        String,
        nullable=True,
    )

    stripe_session_id = Column(
        String,
        unique=True,
        nullable=True,
    )

    stripe_payment_intent_id = Column(
        String,
        nullable=True,
    )
    # =========================
    # FINANCIAL
    # =========================
    amount = Column(
        Float,
        nullable=False
    )

    currency = Column(
        String,
        default="eur",
        nullable=False
    )

    # =========================
    # STATUS
    # =========================
    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )

    # =========================
    # DESCRIPTION
    # =========================
    description = Column(
        String,
        nullable=True
    )

    # =========================
    # TIMESTAMPS
    # =========================
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    paid_at = Column(
        DateTime,
        nullable=True
    )
    # =========================
    # ORM RELATIONSHIPS
    # =========================
    application = relationship(
        "ApplicationModel",
        back_populates="payment"
    )

    user = relationship(
        "UserModel",
        back_populates="payments"
    )