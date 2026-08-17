from abc import ABC, abstractmethod
from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.auth.domain.entities.user import User
from abc import ABC, abstractmethod
from typing import List, Optional
from modules.auth.domain.enums import UserRole
from modules.sav.application.results.support_ticket_list_item import (
    SupportTicketListItem,
)
from modules.sav.domain.enums import (
    TicketStatus,
    TicketPriority,
    TicketCategory,
)
from typing import Literal

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
        search: str | None,
        status: TicketStatus | list[TicketStatus] | Literal["ALL"],
        category: TicketCategory | Literal["ALL"],
        priority: TicketPriority | Literal["ALL"],
        sort: str,
        archive: bool,
        user_id: str,
        user_role: UserRole,
    ) -> tuple[list[SupportTicketListItem], int]:
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
    def count_open_tickets_by_agent(self, agent_id: str) -> int:
        pass

    # =====================
    # UNREAD SYSTEM
    # =====================

    @abstractmethod
    def count_unread(
        self,
        user_id: str,
        user_role: UserRole,
    ) -> int:
        pass