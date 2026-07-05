from math import ceil

from modules.sav.api.schemas import SupportTicketItemDTO, PaginatedSupportTicketsResponse
from modules.core.enums import TicketFilter, TicketStatus, TicketPriority

from math import ceil

class FindSupportTicketsUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, query, user):

        status = query.status
        priority = query.priority

        # =====================
        # Sidebar filters
        # =====================
        if query.filter == TicketFilter.OPEN:
            status = TicketStatus.OPEN

        elif query.filter == TicketFilter.URGENT:
            priority = TicketPriority.HIGH

        # =====================
        # FETCH TICKETS
        # =====================
        tickets, total = self.repo.find_all(
            page=query.page,
            limit=query.limit,
            search=query.search,
            status=status,
            category=query.category,
            priority=priority,
            sort=query.sort,
            user=user,
        )

        # =====================
        # UNREAD IDS (IMPORTANT)
        # =====================
        unread_ticket_ids = set(
            self.repo.get_unread_ticket_ids(user)
        )

        # =====================
        # DTO MAPPING
        # =====================
        items = []

        for ticket in tickets:
            dto = SupportTicketItemDTO.model_validate(ticket)

            dto.unread = ticket.id in unread_ticket_ids

            items.append(dto)

        return PaginatedSupportTicketsResponse(
            items=items,
            page=query.page,
            limit=query.limit,
            total=total,
            pages=1 if total == 0 else ceil(total / query.limit),
        )