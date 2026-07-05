from modules.sav.domain.entities.ticket_read_state import TicketReadState
from modules.sav.infrastructure.db.ticket_read_state_model import TicketReadStateModel

class TicketReadStateMapper:

    @staticmethod
    def to_domain(model: TicketReadStateModel) -> TicketReadState:
        return TicketReadState(
            ticket_id=model.ticket_id,
            user_id=model.user_id,
            last_read_at=model.last_read_at,
        )

    @staticmethod
    def to_model(entity: TicketReadState) -> TicketReadStateModel:
        return TicketReadStateModel(
            ticket_id=entity.ticket_id,
            user_id=entity.user_id,
            last_read_at=entity.last_read_at,
        )