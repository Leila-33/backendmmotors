from abc import ABC, abstractmethod

from modules.sav.domain.entities.ticket_read_state import TicketReadState
from datetime import datetime
from modules.auth.domain.entities.user import User
class TicketReadStateRepository(ABC):

    @abstractmethod
    def get(
        self,
        ticket_id: str,
        user_id: str,
    ) -> TicketReadState | None:
        pass

    @abstractmethod
    def save(
        self,
        state: TicketReadState,
    ) -> TicketReadState:
        pass

    @abstractmethod
    def mark_last_read(
        self,
        ticket_id: str,
        user_id: str,
        last_read_at: datetime
    ) -> TicketReadState:
        pass

    @abstractmethod
    def delete_by_ticket(
        self,
        ticket_id: str,
    ) -> None:
        pass