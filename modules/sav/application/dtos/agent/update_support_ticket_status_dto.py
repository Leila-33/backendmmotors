from dataclasses import dataclass

from modules.sav.domain.enums import TicketStatus


@dataclass(frozen=True)
class UpdateSupportTicketStatusDTO:

    ticket_id: str
    status: TicketStatus
    user_id: str