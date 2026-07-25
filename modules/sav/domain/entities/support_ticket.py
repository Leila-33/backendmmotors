from dataclasses import dataclass, field
from datetime import datetime
from modules.sav.domain.entities.ticket_message import TicketMessage
from modules.sav.domain.enums import TicketCategory, TicketPriority, TicketStatus

@dataclass
class SupportTicket:
    id: str
    user_id: str
    application_id: str | None

    subject: str
    description: str
    category: TicketCategory
    status: TicketStatus
    priority: TicketPriority

    assigned_to: str | None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    messages: list["TicketMessage"] = field(default_factory=list)
    archived_at: datetime | None = None