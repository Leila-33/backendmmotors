from dataclasses import dataclass


@dataclass
class CreateTicketMessageDTO:

    ticket_id: str
    message: str