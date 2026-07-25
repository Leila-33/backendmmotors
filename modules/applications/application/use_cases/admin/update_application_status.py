from modules.applications.api.schemas import UpdateApplicationStatusDTO, UpdateApplicationStatusResponseDTO
from modules.applications.domain.exceptions import ApplicationNotFound
from uuid import uuid4
from datetime import datetime, timezone
from modules.applications.domain.entities.event import Event
from modules.applications.domain.repositories.event_repository import EventRepository
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.notifications.domain.enums import NotificationEntityType, NotificationType


class UpdateApplicationStatusUseCase:

    def __init__(
        self,
        application_repository,
        notification_service,
        event_repository: EventRepository
    ):
        self.application_repository = application_repository
        self.notification_service = notification_service
        self.event_repository = event_repository

    async def execute(self, application_id: str, dto: UpdateApplicationStatusDTO):

        # =========================
        # GET APPLICATION
        # =========================
        application = self.application_repository.get_by_id(application_id)

        if not application:
            raise ApplicationNotFound()

        old_status = application.status

        # =========================
        # UPDATE STATUS
        # =========================
        application.status = dto.status

        self.application_repository.update(application)

        # =========================
        # NOTIFICATION
        # =========================
        notif = self._build_notification(
                application,
                dto.status,
                dto.reason
            )
        await self.notification_service.send(
            user_id=application.user_id,
            email=application.email,
            entity_type=NotificationEntityType.APPLICATION,
            entity_id=application.id,
            title=notif["title"],
            message=notif["message"],
            notif_type=notif["type"]
        )

        # =========================
        # EVENT (AUDIT TRAIL)
        # =========================
        event_type = self._map_status_to_event(dto.status)

        event = Event(
            id=str(uuid4()),
            application_id=application.id,
            type=event_type,
            message=notif["message"],
            user_id=application.user_id,
            event_metadata={
                "old_status": old_status.value if old_status else None,
                "new_status": dto.status.value,
                "reason": dto.reason
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
        return UpdateApplicationStatusResponseDTO(
            application_id=application.id,
            status=application.status.value,
            message=notif["message"]
        )

    # =========================
    # NOTIFICATION MAP
    # =========================

    def _build_notification(self, application, status, reason: str | None = None):

        application_number = application.id[:8].upper()

        user_first_name = getattr(application.user, "first_name", "cher client")

        base_intro = (
            f"Bonjour {user_first_name},\n\n"
            f"Votre dossier n°{application_number} "
        )

        # =========================
        # APPROVED
        # =========================
        if status == ApplicationStatus.APPROVED:

            message = (
                base_intro +
                "a été validé avec succès.\n\n"
                "Vous pouvez désormais suivre les prochaines étapes depuis votre espace client.\n\n"
                "Nous vous remercions pour votre confiance.\n\n"
                "Cordialement,\n"
                "L’équipe Mmotors"
            )

            return {
                "title": "Dossier validé",
                "message": message,
                "type": NotificationType.APPLICATION_APPROVED
            }

        # =========================
        # REJECTED
        # =========================
        if status == ApplicationStatus.REJECTED:

            message = (
                base_intro +
                "a été refusé.\n\n"
            )

            if reason:
                message += f"Motif : {reason}\n\n"

            message += (
                "Vous pouvez modifier votre dossier et le soumettre à nouveau.\n\n"
                "Cordialement,\n"
                "L’équipe Mmotors"
            )

            return {
                "title": "Dossier refusé",
                "message": message,
                "type": NotificationType.APPLICATION_REJECTED
            }

        # =========================
        # DEFAULT
        # =========================
        message = (
            base_intro +
            "a été mis à jour.\n\n"
            "Cordialement,\n"
            "L’équipe Mmotors"
        )

        return {
            "title": "Dossier mis à jour",
            "message": message,
            "type": NotificationType.APPLICATION_UPDATED
        }
    
    def _map_status_to_event(self, status):

        if status == ApplicationStatus.APPROVED:
            return EventType.APPLICATION_APPROVED

        if status == ApplicationStatus.REJECTED:
            return EventType.APPLICATION_REJECTED

        if status == ApplicationStatus.SUBMITTED:
            return EventType.APPLICATION_SUBMITTED

        return EventType.APPLICATION_SUBMITTED