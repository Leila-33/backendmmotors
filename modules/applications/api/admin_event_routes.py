from fastapi import APIRouter, Depends
from modules.applications.application.use_cases.admin.get_events import GetEventsUseCase
from modules.applications.api.dependencies import get_events_usecase
from modules.applications.api.schemas import EventPaginationResponse

router = APIRouter(tags=["Admin Events"])



@router.get(
    "",
    response_model=EventPaginationResponse
)
def get_events(
    page: int = 1,
    limit: int = 20,
    search: str | None = None,
    type: str | None = None,
    date: str | None = None,

    uc: GetEventsUseCase = Depends(
        get_events_usecase
    )
):


    return uc.execute(

        page=page,

        limit=limit,

        search=search,

        event_type=type,

        date=date
    )