from datetime import datetime, timezone
import uuid

from modules.applications.domain.entities.application import ApplicationStatus
from modules.applications.domain.entities.application_event import ApplicationEvent
from modules.notifications.domain.entities.notification import NotificationType


class RejectApplication:

    def __init__(
        self,
        application_repo,
        event_repo,
        notification_service
    ):
        self.application_repo = application_repo
        self.event_repo = event_repo
        self.notification_service = notification_service

    def execute(self, application_id: str, admin_id: str, reason: str = None):

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
            raise Exception("APPLICATION_NOT_REJECTABLE")

        now = datetime.now(timezone.utc)

        # =====================
        # 3. UPDATE STATUS
        # =====================
        application.status = ApplicationStatus.REJECTED
        self.application_repo.update(application)

        # =====================
        # 4. EVENT (AUDIT)
        # =====================
        message = "Dossier refusé par l’administrateur"
        if reason:
            message += f" : {reason}"

        event = ApplicationEvent(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type="REJECTED",
            message=message,
            created_at=now,
            user_id=admin_id
        )

        self.event_repo.save(event)

        # =====================
        # 5. NOTIFICATION + EMAIL
        # =====================
        notif_message = "Votre dossier a été refusé."
        if reason:
            notif_message += f" Motif : {reason}"

        self.notification_service.send(
            user_id=application.user_id,
            email=application.email,
            application_id=application.id,
            title="Dossier refusé",
            message=notif_message,
            notif_type=NotificationType.APPLICATION_REJECTED
        )

        # =====================
        # 6. RESPONSE
        # =====================
        return {
            "id": application.id,
            "status": application.status.value,
            "message": "Dossier refusé avec succès"
        }