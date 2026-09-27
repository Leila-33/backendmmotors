import uuid

from modules.applications.domain.enums import EventType
from modules.applications.domain.entities.event import Event
from modules.applications.domain.repositories.event_repository import (
    EventRepository,
)


class EventService:
    """
    Crée et enregistre les événements liés aux actions effectuées
    dans l'application.

    Un événement peut être associé à un utilisateur, un dossier,
    un essai routier, un véhicule, un devis ou un lead.
    """
    def __init__(
        self,
        event_repository: EventRepository,
    ):
        self.event_repository = event_repository

    def log(
        self,
        type: EventType,
        message: str,
        user_id: str | None = None,
        application_id: str | None = None,
        test_drive_id: str | None = None,
        vehicle_id: str | None = None,
        quote_id: str | None = None,
        lead_id: str | None = None,
        event_metadata: dict | None = None,
    ) -> Event:
        """
        Crée et enregistre un événement avec les ressources
        auxquelles il est associé.
        """
        event = Event(
            id=str(uuid.uuid4()),
            type=type,
            message=message,
            event_metadata=event_metadata,
            user_id=user_id,
            vehicle_id=vehicle_id,
            quote_id=quote_id,
            application_id=application_id,
            test_drive_id=test_drive_id,
            lead_id=lead_id,
        )

        return self.event_repository.save(event)