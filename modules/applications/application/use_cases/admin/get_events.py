from modules.applications.domain.enums import EventCategory
from core.pagination.paginated_result import PaginatedResult


class GetEventsUseCase:

    def __init__(
        self,
        event_repository,
    ):
        self.event_repository = event_repository

    def execute(
        self,
        page: int,
        limit: int,
        search: str | None = None,
        event_category: EventCategory | None = None,
        date: str | None = None,
    ) -> PaginatedResult:

        events, total = (
            self.event_repository.find_all(
                page=page,
                limit=limit,
                search=search,
                event_category=event_category,
                date=date,
            )
        )

        return PaginatedResult.create(
            items=events,
            total=total,
            page=page,
            limit=limit,
        )