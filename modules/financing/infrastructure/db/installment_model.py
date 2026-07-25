from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    ForeignKey,
    Enum,
    Integer
)
from sqlalchemy.orm import relationship

from datetime import datetime, timezone

from core.database.session import Base

from modules.payments.domain.enums import InstallmentStatus


class InstallmentPaymentModel(Base):

    __tablename__ = "installments"

    # =========================
    # PRIMARY KEY
    # =========================
    id = Column(
        String,
        primary_key=True
    )

    financing_contract_id = Column(
        String,
        ForeignKey(
            "financing_contracts.id"
        ),
        nullable=False
    )

    installment_number = Column(
    Integer,
    nullable=False
)

    # =========================
    # AMOUNT
    # =========================
    amount = Column(
        Float,
        nullable=False
    )

    # =========================
    # DUE DATE
    # =========================
    due_date = Column(
        DateTime,
        nullable=False
    )

    paid_at = Column(
        DateTime,
        nullable=True
    )

    # =========================
    # STATUS (ENUM)
    # =========================
    status = Column(
        Enum(InstallmentStatus),
        nullable=False,
        default=InstallmentStatus.PENDING
    )

    # =========================
    # STRIPE
    # =========================
    stripe_invoice_id = Column(
        String,
        nullable=True
    )

    # =========================
    # TIMESTAMPS
    # =========================
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(
            timezone.utc
        )
    )

    financing_contract = relationship(
    "FinancingContractModel",
    back_populates="installments"
)