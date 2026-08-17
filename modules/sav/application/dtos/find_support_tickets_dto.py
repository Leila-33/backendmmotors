from dataclasses import dataclass

from modules.sav.domain.enums import (
    TicketStatus,
    TicketPriority,
    TicketCategory,
    TicketFilter,
)


@dataclass(frozen=True)
class FindSupportTicketsDTO:

    page: int = 1
    limit: int = 10

    search: str = ""

    status: TicketStatus | str = "ALL"

    priority: TicketPriority | str = "ALL"

    category: TicketCategory | str = "ALL"

    sort: str = "created_at_desc"

    filter: TicketFilter = TicketFilter.ALL

    archive: bool = False