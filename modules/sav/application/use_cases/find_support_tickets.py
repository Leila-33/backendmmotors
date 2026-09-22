from modules.sav.application.dtos.find_support_tickets_dto import (
    FindSupportTicketsDTO,
)

from modules.sav.domain.enums import (
    TicketStatus,
    TicketPriority,
    TicketFilter,
)
from core.pagination.paginated_result import PaginatedResult


class FindSupportTicketsUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(
        self,
        dto: FindSupportTicketsDTO,
        user_id: str,
        user_role,
    ) -> PaginatedResult:

        status = dto.status
        priority = dto.priority

        if dto.filter == TicketFilter.OPEN:
            status = [
                TicketStatus.OPEN,
                TicketStatus.IN_PROGRESS,
                TicketStatus.WAITING_CUSTOMER,
            ]

        elif dto.filter == TicketFilter.URGENT:
            priority = TicketPriority.URGENT

        items, total = self.repo.find_all(
            page=dto.page,
            limit=dto.limit,
            search=dto.search,
            status=status,
            category=dto.category,
            priority=priority,
            sort=dto.sort,
            archive=dto.archive,
            user_id=user_id,
            user_role=user_role,
        )

        return PaginatedResult.create(
            items=items,
            page=dto.page,
            limit=dto.limit,
            total=total,
        )