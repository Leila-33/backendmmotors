from modules.sav.domain.entities.ticket_message import TicketMessage
from modules.sav.infrastructure.db.ticket_message_model import TicketMessageModel


class TicketMessageMapper:

    @staticmethod
    def to_domain(model):
        return TicketMessage(
            id=model.id,
            ticket_id=model.ticket_id,
            sender_id=model.sender_id,
            sender_role=model.sender_role,
            message=model.message,
            created_at=model.created_at
        )

    @staticmethod
    def to_model(domain):
        return TicketMessageModel(
            id=domain.id,
            ticket_id=domain.ticket_id,
            sender_id=domain.sender_id,
            sender_role=domain.sender_role,
            message=domain.message,
            created_at=domain.created_at
        )