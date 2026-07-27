from modules.sav.domain.repositories.ticket_message_repository import TicketMessageRepository
from modules.sav.infrastructure.db.ticket_message_model import TicketMessageModel
from modules.sav.infrastructure.mappers.ticket_message_mapper import TicketMessageMapper
from sqlalchemy.orm import Session
from sqlalchemy import asc
from modules.sav.infrastructure.mappers.ticket_message_mapper import (
    TicketMessageMapper,
)


class TicketMessageSQLRepository(TicketMessageRepository):

    def __init__(self, session: Session):
        self.session = session

    # =========================
    # GET BY TICKET
    # =========================
    def get_by_ticket(
        self,
        ticket_id: str
    ):

        models = (
            self.session.query(TicketMessageModel)
            .filter(
                TicketMessageModel.ticket_id == ticket_id
            )
            .order_by(
                asc(TicketMessageModel.created_at)
            )
            .all()
        )

        return [
            TicketMessageMapper.to_domain(model)
            for model in models
        ]

    # =========================
    # CREATE
    # =========================
    def create(
        self,
        message
    ):

        model = TicketMessageMapper.to_model(message)

        self.session.add(model)

        return TicketMessageMapper.to_domain(model)