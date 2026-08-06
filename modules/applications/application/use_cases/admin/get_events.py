import math
from modules.applications.api.schemas import (
    EventPaginationResponse,
    EventDetailResponse
)

class GetEventsUseCase:

    def __init__(
        self,
        event_repository
    ):
        self.event_repository = event_repository


    def execute(
        self,
        page,
        limit,
        search=None,
        event_type=None,
        date=None
    ):

        events, total = (
            self.event_repository.find_all(
                page=page,
                limit=limit,
                search=search,
                event_type=event_type,
                date=date
            )
        )


        items = [
            EventDetailResponse(
                id=event.id,
                type=event.type.value,
                message=event.message,
                event_metadata=event.event_metadata,
                created_at=event.created_at,
                application_id=event.application_id,
                test_drive_id=event.test_drive_id,
                user_id=event.user_id,
            )
            for event in events
        ]


        total_pages = math.ceil(
            total / limit
        )


        return EventPaginationResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )