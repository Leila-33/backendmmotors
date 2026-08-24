
from core.database.session import Base
from modules.leads.domain.enums import LeadStatus
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class LeadModel(Base):

    __tablename__ = "leads"


    # =====================================================
    # IDENTIFIERS
    # =====================================================

    id = Column(
        String,
        primary_key=True,
        index=True
    )


    vehicle_id = Column(
        String,
        ForeignKey("vehicles.id"),
        nullable=False
    )


    # Client connecté (optionnel)
    # NULL si le visiteur n'a pas encore de compte
    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=True
    )


    # Agent commercial assigné
    assigned_to = Column(
        String,
        ForeignKey("users.id"),
        nullable=True
    )



    # =====================================================
    # CUSTOMER INFO
    # =====================================================

    first_name = Column(
        String,
        nullable=False
    )


    last_name = Column(
        String,
        nullable=False
    )


    email = Column(
        String,
        index=True,
        nullable=False
    )


    phone = Column(
        String,
        nullable=True
    )


    message = Column(
        Text,
        nullable=True
    )



    # =====================================================
    # STATUS CRM PIPELINE
    # =====================================================

    status = Column(
        Enum(LeadStatus),
        default=LeadStatus.NEW,
        nullable=False,
        index=True
    )



    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )



    # =====================================================
    # RELATIONS
    # =====================================================


    # Véhicule intéressé
    vehicle = relationship(
        "VehicleModel",
        back_populates="leads",
    )



    # Client propriétaire du lead
    customer = relationship(
        "UserModel",
        foreign_keys=[user_id],
        back_populates="leads",
    )



    # Commercial responsable
    assigned_agent = relationship(
        "UserModel",
        foreign_keys=[assigned_to],
        back_populates="assigned_leads",
    )

    quotes = relationship(
    "QuoteModel",
    back_populates="lead",
    cascade="all, delete-orphan",
)
    events = relationship(
        "EventModel",
        back_populates="lead",
    )
    # =====================================================
    # INDEXES
    # =====================================================

    __table_args__ = (

        Index(
            "ix_leads_email",
            "email"
        ),

        Index(
            "ix_leads_vehicle_id",
            "vehicle_id"
        ),

        Index(
            "ix_leads_status",
            "status"
        ),

        Index(
            "ix_leads_user_id",
            "user_id"
        ),

        Index(
            "ix_leads_assigned_to",
            "assigned_to"
        ),
    )