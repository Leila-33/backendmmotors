from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from core.database.session import Base


from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class UserActivationTokenModel(Base):

    __tablename__ = "user_activation_tokens"


    id = Column(
        String,
        primary_key=True,
    )


    user_id = Column(
        String,
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )


    # =========================
    # CONTEXT
    # =========================

    quote_id = Column(
        String,
        ForeignKey(
            "quotes.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )


    # =========================
    # TOKEN
    # =========================

    token_hash = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )


    # =========================
    # LIFETIME
    # =========================

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )


    used_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )


    created_at = Column(
        DateTime(timezone=True),
        default=lambda:
            datetime.now(timezone.utc),
        nullable=False,
    )


    # =========================
    # RELATIONS
    # =========================

    user = relationship(
        "UserModel",
        back_populates="activation_tokens",
    )


    quote = relationship(
        "QuoteModel",
        back_populates="activation_tokens",
    )