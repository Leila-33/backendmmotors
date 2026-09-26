from modules.applications.infrastructure.db.event_model import EventModel
from modules.applications.domain.entities.event import Event
from modules.applications.api.schemas import EventDetailResponse
from modules.applications.domain.enums import EventType



class EventMapper:


    @staticmethod
    def to_domain(
        model: EventModel
    ) -> Event:

        return Event(

            id=model.id,

            type=EventType(model.type),

            message=model.message,

            event_metadata=(
                model.event_metadata
                if model.event_metadata
                else {}
            ),

            created_at=model.created_at,

            application_id=model.application_id,

            test_drive_id=model.test_drive_id,

            user_id=model.user_id,
        )


    @staticmethod
    def to_model(
        event: Event
    ) -> EventModel:

        return EventModel(

            id=event.id,

            type=event.type.value,

            message=event.message,

            event_metadata=(
                event.event_metadata
                if event.event_metadata
                else {}
            ),

            created_at=event.created_at,

            application_id=event.application_id,

            test_drive_id=event.test_drive_id,

            user_id=event.user_id,
        )


    @staticmethod
    def update_model(
        model: EventModel,
        event: Event,
    ) -> EventModel:


        model.type = (
            event.type
        )

        model.message = (
            event.message
        )

        model.event_metadata = (
            event.event_metadata
        )

        return model



    @staticmethod
    def to_response(
        event: Event
    ) -> EventDetailResponse:

        return EventDetailResponse(

            id=event.id,

            type=event.type,

            message=event.message,

            event_metadata=(
                event.event_metadata
            ),

            created_at=event.created_at,

            application_id=(
                event.application_id
            ),

            test_drive_id=(
                event.test_drive_id
            ),

            user_id=(
                event.user_id
            ),
        )