from dataclasses import dataclass
from datetime import datetime
from modules.auth.domain.enums import UserRole

@dataclass
class TicketMessage:
    id: str
    ticket_id: str
    sender_id: str
    sender_role: UserRole
    message: str
    created_at: datetime | None = None
