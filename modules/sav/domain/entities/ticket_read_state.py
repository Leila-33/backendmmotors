from dataclasses import dataclass
from datetime import datetime


@dataclass
class TicketReadState:
    ticket_id: str
    user_id: str

    last_read_at: datetime | None = None