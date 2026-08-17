from dataclasses import dataclass

from modules.sav.domain.entities.ticket_message import TicketMessage


@dataclass
class CreateTicketMessageResult:

    message: TicketMessage