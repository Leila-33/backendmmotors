from dataclasses import dataclass

from modules.sav.domain.entities.support_ticket import SupportTicket


@dataclass
class CreateSupportTicketResult:

    ticket: SupportTicket