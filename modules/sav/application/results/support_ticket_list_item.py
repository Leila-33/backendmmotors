from dataclasses import dataclass
from datetime import datetime
from modules.sav.domain.enums import (
    TicketCategory,
    TicketPriority,
    TicketStatus
)

@dataclass
class SupportTicketListItem:
    id: str
    subject: str
    category: TicketCategory
    status: TicketStatus
    priority: TicketPriority
    user_id: str
    user_name: str | None
    last_message_preview: str | None
    last_actor: str | None
    last_activity_at: datetime | None
    unread: bool
    created_at: datetime
    updated_at: datetime | None
    archived_at: datetime | None