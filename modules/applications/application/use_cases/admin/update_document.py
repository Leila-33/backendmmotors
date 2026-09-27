import logging

from core.database.unit_of_work import UnitOfWork

from modules.applications.application.dtos.admin.update_document_dto import (
    UpdateDocumentDTO,
)
from modules.applications.application.results.admin.update_document_result import (
    UpdateDocumentResult,
)

from modules.applications.domain.builders.document_message_builder import (
    DocumentMessageBuilder,
)
from modules.applications.domain.builders.document_notification_builder import (
    DocumentNotificationBuilder,
)
from modules.applications.domain.document_messages import (
    DOCUMENT_EVENT_MAP,
)
from modules.applications.domain.enums import (
    DocumentStatus,
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
    DocumentNotFound,
)

from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType,
)


logger = logging.getLogger(__name__)


class UpdateDocumentUseCase:
    """
    Met à jour le statut et le commentaire d'un document d'un dossier,
    puis enregistre l'action dans l'historique et notifie le client
    lorsque le document est rejeté.
    """
    def __init__(
        self,
        document_repository,
        application_repository,
        event_service,
        notification_service,
        uow: UnitOfWork,
    ):
        self.document_repository = document_repository
        self.application_repository = application_repository
        self.event_service = event_service
        self.notification_service = notification_service
        self.uow = uow

    async def execute(
        self,
        dto: UpdateDocumentDTO,
        current_admin,
    ):
        document = None
        application = None

        try:
            # =================================================
            # GET DOCUMENT
            # =================================================

            document = self.document_repository.get_by_id(
                dto.document_id
            )

            if not document:
                raise DocumentNotFound()

            # =================================================
            # GET APPLICATION
            # =================================================

            application = self.application_repository.get_by_id(
                document.application_id
            )

            if not application:
                raise ApplicationNotFound()

            # =================================================
            # UPDATE DOCUMENT
            # =================================================

            document.update_status(
                status=dto.status,
                comment=dto.comment,
            )

            self.document_repository.save(document)

            # =================================================
            # EVENT
            # =================================================

            event_type = DOCUMENT_EVENT_MAP.get(dto.status)

            if event_type:
                message = DocumentMessageBuilder.build(
                    document_type=document.type,
                    status=dto.status,
                    comment=dto.comment,
                )

                self.event_service.log(
                    application_id=document.application_id,
                    type=event_type,
                    message=message,
                    user_id=current_admin.id,
                    vehicle_id=application.vehicle_id,
                    event_metadata={
                        "document_id": document.id,
                        "document_type": document.type,
                        "status": dto.status.value,
                    },
                )

            # =================================================
            # NOTIFICATION
            # =================================================

            if dto.status == DocumentStatus.REJECTED:

                notification = (
                    DocumentNotificationBuilder.build_rejected(
                        document_type=document.type,
                        comment=dto.comment,
                    )
                )

                await self.notification_service.send(
                    user_id=application.user_id,
                    email=application.user.email,
                    entity_type=NotificationEntityType.APPLICATION,
                    entity_id=document.application_id,
                    title=notification.title,
                    message=notification.message,
                    notif_type=NotificationType.DOCUMENT_REJECTED,
                )

            # =================================================
            # COMMIT
            # =================================================

            self.uow.commit()

            logger.info(
                "Document application mis à jour",
                extra={
                    "application_id": application.id,
                    "document_id": document.id,
                    "admin_id": current_admin.id,
                },
            )

            # =================================================
            # RESULT
            # =================================================

            return UpdateDocumentResult(
                document_id=document.id,
                status=document.status,
                comment=document.comment,
            )

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur lors de la mise à jour d'un document",
                extra={
                    "application_id": (
                        application.id
                        if application
                        else None
                    ),
                    "document_id": (
                        document.id
                        if document
                        else dto.document_id
                    ),
                },
            )

            raise