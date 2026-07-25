from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from core.database.session import Base


class FavoriteModel(Base):
    __tablename__ = "favorites"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "vehicle_id",
            name="uq_user_vehicle_favorite"
        ),
    )

    # =========================
    # PRIMARY KEY
    # =========================
    id = Column(String, primary_key=True)

    # =========================
    # FOREIGN KEYS
    # =========================
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

    # =========================
    # METADATA
    # =========================
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # =========================
    # RELATIONSHIPS
    # =========================
    user = relationship(
        "UserModel",
        back_populates="favorites"
    )

    vehicle = relationship(
        "VehicleModel",
        back_populates="favorites"
    )