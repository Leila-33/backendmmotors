from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    Enum,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from core.database.session import Base
from modules.quotes.domain.enums import QuoteStatus, QuoteRefusalReason

class QuoteModel(Base):

    __tablename__ = "quotes"

    id = Column(
        String,
        primary_key=True,
        index=True,
    )

    lead_id = Column(
        String,
        ForeignKey("leads.id"),
        nullable=False,
        index=True,
    )

    base_price = Column(
        Float,
        nullable=False,
    )

    discount = Column(
        Float,
        default=0,
    )

    down_payment = Column(
        Float,
        default=0,
    )

    trade_in_value = Column(
        Float,
        default=0,
    )

    financed_amount = Column(
        Float,
        nullable=False,
    )

    duration_months = Column(
        Integer,
        nullable=False,
    )

    monthly_payment = Column(
        Float,
        nullable=False,
    )

    status = Column(
        Enum(QuoteStatus),
        default=QuoteStatus.DRAFT,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    accepted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    refusal_reason = Column(
    Enum(
        QuoteRefusalReason,
    ),
    nullable=True,
)

    refusal_comment = Column(
        String,
        nullable=True,
    )

    refused_at = Column(
        DateTime(timezone=True),
        nullable=True,
)
    expires_at = Column(
            DateTime(timezone=True),
            nullable=True,
    )


    # Relations

    lead = relationship(
    "LeadModel",
    back_populates="quotes",
)

    trade_in = relationship(
    "QuoteTradeInModel",
    back_populates="quote",
    uselist=False,
    cascade="all, delete-orphan",
)
    activation_tokens = relationship(
    "UserActivationTokenModel",
    back_populates="quote",
)
    application = relationship(
    "ApplicationModel",
    back_populates="quote",
    uselist=False
)