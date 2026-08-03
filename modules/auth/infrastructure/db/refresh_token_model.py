from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, func
from core.database.session import Base
from modules.auth.domain.enums import UserRole


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String, primary_key=True)

    user_id = Column(
        String,
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )

    jti = Column(String, unique=True, index=True, nullable=False)

    # =========================
    # ENUM SAFE DB
    # =========================
    role = Column(
        Enum(UserRole),
        nullable=False
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    revoked = Column(Boolean, default=False, nullable=False)

    # =========================
    # TIMESTAMPS (CLEAN)
    # =========================
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )