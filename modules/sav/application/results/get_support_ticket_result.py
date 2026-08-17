from dataclasses import dataclass

from modules.sav.domain.entities.support_ticket import (
    SupportTicket,
)


@dataclass(frozen=True)
class GetSupportTicketResult:

    ticket: SupportTicket
    unread_count: int