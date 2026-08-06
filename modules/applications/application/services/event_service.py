from modules.applications.domain.enums import EventType
from modules.applications.domain.entities.event import Event
import uuid

class EventService:

    def __init__(
        self,
        event_repository
    ):
        self.event_repository = event_repository


    def log(
        self,
        type: EventType,
        message: str,
        user_id: str | None = None,
        application_id: str | None = None,
        vehicle_id: str | None = None,
        test_drive_id: str | None = None,
        metadata: dict | None = None,
    ):

        event = Event(
            id=str(uuid.uuid4()),
            type=type,
            message=message,
            user_id=user_id,
            application_id=application_id,
            vehicle_id=vehicle_id,
            test_drive_id=test_drive_id,
            event_metadata=metadata,
        )

        return self.event_repository.save(event)