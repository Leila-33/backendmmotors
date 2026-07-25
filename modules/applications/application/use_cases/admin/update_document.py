from datetime import datetime, timezone
from uuid import uuid4

from modules.applications.domain.enums import DocumentStatus, EventType
from modules.notifications.domain.enums import NotificationType, NotificationEntityType

from modules.applications.api.schemas import (
    UpdateDocumentDTO,
    UpdateDocumentResponseDTO
)

from modules.applications.domain.entities.event import Event



DOCUMENT_LABELS = {
    "identity": {
        "label": "Pièce d'identité",
        "gender": "f"
    },
    "payslip": {
        "label": "Bulletin de salaire",
        "gender": "m"
    },
    "rib": {
        "label": "RIB",
        "gender": "m"
    },
    "address_proof": {
        "label": "Justificatif de domicile",
        "gender": "m"
    }
}

STATUS_MESSAGES = {
    DocumentStatus.VALIDATED: {
        "m": "a été validé",
        "f": "a été validée"
    },
    DocumentStatus.REJECTED: {
        "m": "a été refusé",
        "f": "a été refusée"
    },
}

DOCUMENT_EVENT_MAP = {
    DocumentStatus.VALIDATED: EventType.DOCUMENT_VALIDATED,
    DocumentStatus.REJECTED: EventType.DOCUMENT_REJECTED,
}




class UpdateDocumentUseCase:

    def __init__(
        self,
        document_repository,
        event_repository,
        notification_service
    ):

        self.document_repository = document_repository
        self.event_repository = event_repository
        self.notification_service = notification_service

    async def execute(
        self,
        dto: UpdateDocumentDTO,
        current_admin
    ):

        # =========================
        # UPDATE DOCUMENT
        # =========================
        document = self.document_repository.update_status(
            document_id=dto.document_id,
            status=dto.status,
            comment=dto.comment
        )

        # =========================
        # DOCUMENT CONFIG
        # =========================
        document_config = DOCUMENT_LABELS.get(
            document.type,
            {
                "label": document.type,
                "gender": "m"
            }
        )

        label = document_config["label"]
        gender = document_config["gender"]

        # =========================
        # MESSAGE
        # =========================
        message = (
            f"{label} "
            f"{STATUS_MESSAGES[dto.status][gender]}"
        )

        if dto.comment:
            message += f" : {dto.comment}"

        # =========================
        # EVENT
        # =========================
        event_type = DOCUMENT_EVENT_MAP[dto.status]

        event = Event(
            id=str(uuid4()),

            application_id=document.application_id,

            type=event_type,

            message=message,

            user_id=current_admin.id,

            event_metadata={
                "document_id": document.id,
                "document_type": document.type,
                "status": dto.status.value
            },

            created_at=datetime.now(timezone.utc)
        )

        self.event_repository.save(event)

        # =========================
        # NOTIFICATION ONLY IF REJECTED
        # =========================
        if dto.status == DocumentStatus.REJECTED:

            notif_message = (
                f"Bonjour,\n\n"
                f"Votre document « {label} » a été refusé."
            )

            if dto.comment:
                notif_message += (
                    f"\n\nMotif : {dto.comment}"
                )

            notif_message += (
                f"\n\nMerci de le corriger et de le renvoyer "
                f"depuis votre espace client.\n\n"
                f"Cordialement,\n"
                f"L’équipe Mmotors"
            )

            await self.notification_service.send(
                user_id=document.application.user_id,
                email=document.application.user.email,
                entity_type=NotificationEntityType.APPLICATION,
                entity_id=document.application_id,
                title=f"{label} refusé",

                message=notif_message,

                notif_type=NotificationType.DOCUMENT_REJECTED
            )

        # =========================
        # COMMIT
        # =========================
        self.document_repository.commit()
        self.event_repository.commit()

        # =========================
        # RESPONSE
        # =========================
        return UpdateDocumentResponseDTO(
            document_id=document.id,
            status=document.status,
            comment=document.comment
        )