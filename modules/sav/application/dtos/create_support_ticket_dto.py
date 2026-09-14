from dataclasses import dataclass

from modules.sav.domain.enums import TicketCategory, TicketPriority


@dataclass
class CreateSupportTicketDTO:
    subject: str
    category: TicketCategory
    message: str
    priority: TicketPriority
    application_id: str | None