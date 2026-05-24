from uuid import uuid4
from datetime import datetime, timezone

from modules.applications.domain.entities.event import Event
from modules.core.enums import EventType
from modules.core.exceptions import ApplicationNotFound
class ArchiveApplicationUseCase:

    def __init__(
        self,
        application_repository,
        event_repository
    ):
        self.application_repository = application_repository
        self.event_repository = event_repository

    def execute(self, application_id: str, current_admin):

        # =========================
        # GET APPLICATION (important pour audit)
        # =========================
        application = self.application_repository.get_by_id(application_id)

        if not application:
            raise ApplicationNotFound()

        # =========================
        # ARCHIVE
        # =========================
        self.application_repository.archive(application_id)

        # =========================
        # EVENT (AUDIT TRAIL)
        # =========================
        event = Event(
            id=str(uuid4()),
            application_id=application_id,
            type=EventType.APPLICATION_ARCHIVED,
            message="Dossier archivé par l'administrateur",
            user_id=current_admin.id,
            event_metadata={
                "archived_by": current_admin.id,
                "vehicle_id": application.vehicle_id,
                "status_before": application.status.value if application.status else None
            },
            created_at=datetime.now(timezone.utc)
        )

        self.event_repository.save(event)

        # =========================
        # COMMIT
        # =========================
        self.application_repository.commit()
        self.event_repository.commit()

        # =========================
        # RESPONSE
        # =========================
        return {"success": True}