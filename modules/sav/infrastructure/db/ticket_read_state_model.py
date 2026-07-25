from core.database.session import Base
from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

class TicketReadStateModel(Base):
    __tablename__ = "ticket_read_states"

    ticket_id = Column(
        String,
        ForeignKey("support_tickets.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id = Column(
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    last_read_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    ticket = relationship(
        "SupportTicketModel",
        back_populates="read_states",
    )

    user = relationship(
        "UserModel",
        back_populates="ticket_read_states",
    )