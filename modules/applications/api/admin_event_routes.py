from fastapi import APIRouter, Depends, Query

# ============================================================
# Application — Use Cases
# ============================================================

from modules.applications.application.use_cases.admin.get_events import (
    GetEventsUseCase,
)


# ============================================================
# API — Dependencies
# ============================================================

from modules.applications.api.dependencies import (
    get_events_usecase,
)


# ============================================================
# API — Schemas
# ============================================================

from modules.applications.api.schemas import (
    EventDetailResponse,
)

# ============================================================
# Pagination
# ============================================================

from core.pagination.paginated_response import PaginatedResponse

# ============================================================
# Enum
# ============================================================
from modules.applications.domain.enums import EventCategory

# ============================================================
# Mapper
# ============================================================
from modules.applications.infrastructure.mappers.event_mapper import EventMapper

# ============================================================
# Router
# ============================================================

router = APIRouter(
    tags=["Admin Events"],
)


# ============================================================
# GET EVENTS
# ============================================================
@router.get(
    "",
    response_model=PaginatedResponse[
        EventDetailResponse
    ],
)
def get_events(
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
    ),
    event_category: EventCategory | None = Query(
        default=None,
    ),
    date: str | None = Query(
        default=None,
    ),

    usecase: GetEventsUseCase = Depends(
        get_events_usecase
    ),
):
    result = usecase.execute(
        page=page,
        limit=limit,
        search=search,
        event_category=event_category,
        date=date,
    )

    return PaginatedResponse(
        items=[
            EventMapper.to_response(event)
            for event in result.items
        ],
        total=result.total,
        page=result.page,
        limit=result.limit,
        total_pages=result.total_pages,
    )