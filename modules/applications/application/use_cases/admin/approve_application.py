from datetime import datetime, timezone
import uuid

from modules.applications.domain.entities.application import ApplicationStatus
from modules.applications.domain.entities.application_event import ApplicationEvent
from modules.notifications.domain.entities.notification import NotificationType


class ApproveApplication:

    def __init__(
        self,
        application_repo,
        event_repo,
        notification_service
    ):
        self.application_repo = application_repo
        self.event_repo = event_repo
        self.notification_service = notification_service

    def execute(self, application_id: str, admin_id: str):

        # =====================
        # 1. GET APPLICATION
        # =====================
        application = self.application_repo.get_by_id(application_id)

        if not application:
            raise Exception("APPLICATION_NOT_FOUND")

        # =====================
        # 2. BUSINESS RULE
        # =====================
        if application.status != ApplicationStatus.SUBMITTED:
            raise Exception("APPLICATION_NOT_APPROVABLE")

        now = datetime.now(timezone.utc)

        # =====================
        # 3. UPDATE STATUS
        # =====================
        application.status = ApplicationStatus.APPROVED
        self.application_repo.update(application)

        # =====================
        # 4. EVENT (AUDIT TRAIL)
        # =====================
        event = ApplicationEvent(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type="APPROVED",
            message="Dossier approuvé par l’administrateur",
            created_at=now,
            user_id=admin_id
        )
        self.event_repo.save(event)

        # =====================
        # 5. NOTIFICATION + EMAIL (via service)
        # =====================
        self.notification_service.send(
            user_id=application.user_id,
            email=application.email,
            application_id=application.id,
            title="Dossier approuvé",
            message="Votre dossier a été validé avec succès.",
            notif_type=NotificationType.APPLICATION_APPROVED
        )

        # =====================
        # 6. RESPONSE
        # =====================
        return {
            "id": application.id,
            "status": application.status.value,
            "message": "Dossier approuvé avec succès"
        }