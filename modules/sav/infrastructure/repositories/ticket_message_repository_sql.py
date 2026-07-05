from modules.sav.domain.repositories.ticket_message_repository import TicketMessageRepository
from modules.sav.infrastructure.db.ticket_message_model import TicketMessageModel
from modules.sav.domain.entities.ticket_message import TicketMessage
from modules.sav.infrastructure.mappers.ticket_message_mapper import TicketMessageMapper

class TicketMessageSQLRepository(TicketMessageRepository):

    def __init__(self, db):
        self.db = db

    def get_by_ticket(self, ticket_id: str):
        return (
            self.db.query(TicketMessageModel)
            .filter(TicketMessageModel.ticket_id == ticket_id)
            .order_by(TicketMessageModel.created_at.asc())
            .all()
        )

    def create(self, message: TicketMessage):

        model = TicketMessageMapper.to_model(message)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return TicketMessageMapper.to_domain(model)