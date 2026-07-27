from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database.session import Base
from modules.auth.domain.enums import UserRole

class TicketMessageModel(Base):
    __tablename__ = "ticket_messages"

    id = Column(String, primary_key=True)

    ticket_id = Column(
        String,
        ForeignKey("support_tickets.id", ondelete="CASCADE"),
        nullable=False
    )

    sender_id = Column(String, ForeignKey("users.id"), nullable=False)

    sender_role = Column(
        Enum(UserRole),
        nullable=False
    )
    message = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # =====================
    # ORM RELATIONS
    # =====================

    ticket = relationship("SupportTicketModel", back_populates="messages")

    sender = relationship(
        "UserModel",
        foreign_keys=[sender_id]
    )