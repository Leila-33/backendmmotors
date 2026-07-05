from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.db.session import Base
from modules.core.enums import TicketStatus, TicketCategory, TicketPriority

class SupportTicketModel(Base):
    __tablename__ = "support_tickets"

    id = Column(String, primary_key=True)

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    application_id = Column(String, ForeignKey("applications.id"), nullable=True)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(
    SQLEnum(TicketCategory),
    nullable=False
)
    status = Column(
    SQLEnum(TicketStatus),
    nullable=False,
    default=TicketStatus.OPEN
)

    priority = Column(
    SQLEnum(TicketPriority),
    nullable=False,
    default=TicketPriority.MEDIUM
)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # =====================
    # ORM RELATIONS
    # =====================

    user = relationship(
        "UserModel",
        back_populates="tickets",
        foreign_keys=[user_id]
    )
    assignee = relationship(
    "UserModel",
    foreign_keys=[assigned_to]
)
    application = relationship("ApplicationModel", back_populates="tickets")

    messages = relationship(
    "TicketMessageModel",
    back_populates="ticket",
    cascade="all, delete-orphan",
    order_by="TicketMessageModel.created_at.asc()"
)

    read_states = relationship(
        "TicketReadStateModel",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )