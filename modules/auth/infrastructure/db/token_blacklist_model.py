from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
from core.database.session import Base


class TokenBlacklistModel(Base):
    __tablename__ = "token_blacklist"

    id = Column(String, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))