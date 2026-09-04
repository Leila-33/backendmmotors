from dataclasses import dataclass
from modules.sav.application.results.support_ticket_list_item import SupportTicketListItem

@dataclass(frozen=True)
class FindSupportTicketsResult:
    items: list[SupportTicketListItem]
    page: int
    limit: int
    total: int
    pages: int