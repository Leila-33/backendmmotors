from abc import ABC, abstractmethod

from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.auth.domain.entities.user import User
from modules.sav.infrastructure.db.support_ticket_model import SupportTicketModel
from abc import ABC, abstractmethod
from typing import List, Optional
from modules.sav.api.schemas import SupportTicketListItemResponse

class SupportTicketRepository(ABC):

    # =====================
    # CRUD
    # =====================

    @abstractmethod
    def create(self, ticket: SupportTicket) -> SupportTicket:
        pass

    @abstractmethod
    def get_by_id(self, ticket_id: str) -> Optional[SupportTicket]:
        pass

    @abstractmethod
    def update(self, ticket: SupportTicket) -> SupportTicket:
        pass

    # =====================
    # LISTING
    # =====================

    @abstractmethod
    def find_all(
        self,
        page: int,
        limit: int,
        search: str,
        status: str,
        category: str,
        priority: str,
        sort: str,
        user: User,
    ) -> tuple[list[SupportTicketListItemResponse], int]:
        pass

    # =====================
    # STATS
    # =====================

    @abstractmethod
    def get_dashboard_stats(self, user: User):
        pass

    @abstractmethod
    def get_sav_statistics(self, user: User):
        pass

    @abstractmethod
    def count_open(self, user: Optional[User] = None) -> int:
        pass

    @abstractmethod
    def count_open_tickets_by_agent(self, agent_id: str) -> int:
        pass

    # =====================
    # UNREAD SYSTEM
    # =====================

    @abstractmethod
    def count_unread(self, user: User) -> int:
        pass