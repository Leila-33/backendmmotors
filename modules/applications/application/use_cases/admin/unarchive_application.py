from uuid import uuid4
from datetime import datetime, timezone

from modules.applications.domain.entities.event import Event
from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound

class UnarchiveApplicationUseCase:

    def __init__(
        self,
        application_repository,
        event_repository
    ):
        self.application_repository = application_repository
        self.event_repository = event_repository

    def execute(self, application_id: str, current_admin):

        # =========================
        # 1. GET APPLICATION (audit important)
        # =========================
        application = self.application_repository.get_by_id(application_id)

        if not application:
            raise ApplicationNotFound()

        # =========================
        # 2. UNARCHIVE
        # =========================
        self.application_repository.unarchive(application_id)

        # =========================
        # 3. EVENT (AUDIT TRAIL)
        # =========================
        event = Event(
            id=str(uuid4()),
            application_id=application_id,
            type=EventType.APPLICATION_RESTORED,
            message="Dossier restauré depuis les archives",
            user_id=current_admin.id,
            event_metadata={
                "restored_by": current_admin.id,
                "vehicle_id": application.vehicle_id,
                "status_at_restore": application.status.value if application.status else None,
                "was_archived": True
            },
            created_at=datetime.now(timezone.utc)
        )

        self.event_repository.save(event)

        # =========================
        # 4. COMMIT
        # =========================
        self.application_repository.commit()
        self.event_repository.commit()

        # =========================
        # 5. RESPONSE
        # =========================
        return {"success": True}