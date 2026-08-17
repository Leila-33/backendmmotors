from datetime import datetime
from sqlalchemy.orm import Session
from modules.sav.domain.entities.ticket_read_state import TicketReadState
from modules.sav.domain.repositories.ticket_read_state_repository import (
    TicketReadStateRepository,
)
from modules.sav.infrastructure.mappers.ticket_read_state_mapper import (
    TicketReadStateMapper,
)
from modules.sav.infrastructure.db.ticket_read_state_model import (
    TicketReadStateModel,
)





class TicketReadStateRepositorySQL(TicketReadStateRepository):

    def __init__(self, db: Session):
        self.db = db


    # =========================
    # GET
    # =========================
    def get(
        self,
        ticket_id: str,
        user_id: str,
    ) -> TicketReadState | None:

        model = (
            self.db.query(TicketReadStateModel)
            .filter(
                TicketReadStateModel.ticket_id == ticket_id,
                TicketReadStateModel.user_id == user_id,
            )
            .first()
        )

        if not model:
            return None

        return TicketReadStateMapper.to_domain(model)



    # =========================
    # SAVE / UPDATE
    # =========================
    def save(
        self,
        state: TicketReadState,
    ) -> TicketReadState:

        model = (
            self.db.query(TicketReadStateModel)
            .filter(
                TicketReadStateModel.ticket_id == state.ticket_id,
                TicketReadStateModel.user_id == state.user_id,
            )
            .first()
        )


        if model is None:

            model = TicketReadStateMapper.to_model(
                state
            )

            self.db.add(model)

        else:

            model.last_read_at = state.last_read_at


        self.db.flush()
        self.db.refresh(model)

        return TicketReadStateMapper.to_domain(
            model
        )



    # =========================
    # MARK LAST READ
    # =========================
    def mark_last_read(
        self,
        ticket_id: str,
        user_id: str,
        last_read_at: datetime,
    ) -> TicketReadState:

        state = self.get(
            ticket_id,
            user_id,
        )


        if state is None:

            state = TicketReadState(
                ticket_id=ticket_id,
                user_id=user_id,
                last_read_at=last_read_at,
            )

        else:

            state.last_read_at = last_read_at


        return self.save(state)



    # =========================
    # DELETE BY TICKET
    # =========================
    def delete_by_ticket(
        self,
        ticket_id: str,
    ) -> None:

        (
            self.db.query(TicketReadStateModel)
            .filter(
                TicketReadStateModel.ticket_id == ticket_id
            )
            .delete(
                synchronize_session=False
            )
        )

        self.db.flush()