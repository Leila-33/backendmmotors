from dataclasses import dataclass
from datetime import datetime


@dataclass
class TicketMessage:
    id: str
    ticket_id: str
    sender_id: str
    sender_role: str
    message: str
    created_at: datetime | None = None
