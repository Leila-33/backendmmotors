from math import ceil

from modules.sav.api.schemas import PaginatedSupportTicketsResponse
from modules.sav.domain.enums import TicketFilter, TicketStatus, TicketPriority
from modules.sav.infrastructure.mappers.support_ticket_mapper import SupportTicketMapper

from math import ceil

class FindSupportTicketsUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, query, user):

        status = query.status
        priority = query.priority

        if query.filter == TicketFilter.OPEN:

            status = [
                TicketStatus.OPEN,
                TicketStatus.IN_PROGRESS,
                TicketStatus.WAITING_CUSTOMER
            ]

        elif query.filter == TicketFilter.URGENT:
            priority = TicketPriority.URGENT

        rows, total = self.repo.find_all(
            page=query.page,
            limit=query.limit,
            search=query.search,
            status=status,
            category=query.category,
            priority=priority,
            sort=query.sort,
            archive=query.archive,
            user=user,
        )

        items = [
            SupportTicketMapper.from_row(row)
            for row in rows
        ]

        return PaginatedSupportTicketsResponse(
            items=items,
            page=query.page,
            limit=query.limit,
            total=total,
            pages=1 if total == 0 else ceil(total / query.limit),
        )