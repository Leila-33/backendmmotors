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
    EventPaginationResponse,
)


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
    response_model=EventPaginationResponse,
)
def get_events(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = None,
    event_type: str | None = None,
    date: str | None = None,

    usecase: GetEventsUseCase = Depends(
        get_events_usecase
    ),
):
    return usecase.execute(
        page=page,
        limit=limit,
        search=search,
        event_type=event_type,
        date=date,
    )