from modules.applications.api.schemas import (
    UpdateDocumentDTO,
    UpdateDocumentResponseDTO,
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

from modules.applications.domain.enums import DocumentStatus

from modules.applications.domain.exceptions import (
    DocumentNotFound,
    ApplicationNotFound
)

from modules.notifications.domain.enums import (

    NotificationEntityType,
    NotificationType,
)

from core.database.unit_of_work import UnitOfWork
import logging

logger = logging.getLogger(__name__)

class UpdateDocumentUseCase:

    def __init__(
        self,
        document_repository,
        application_repository,
        event_service,
        notification_service,
        uow : UnitOfWork,
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
        try:
            document = self.document_repository.get_by_id(
                dto.document_id
            )

            if not document:
                raise DocumentNotFound()


            application = self.application_repository.get_by_id(
                document.application_id
            )

            if not application:
                raise ApplicationNotFound()

            document.update_status(
                status=dto.status,
                comment=dto.comment,
            )

            self.document_repository.save(document)

            message = DocumentMessageBuilder.build(
                document_type=document.type,
                status=dto.status,
                comment=dto.comment,
            )

            self.event_service.log(
                application_id=document.application_id,
                type=DOCUMENT_EVENT_MAP[dto.status],
                message=message,
                user_id=current_admin.id,
                event_metadata={
                    "document_id": document.id,
                    "document_type": document.type,
                    "status": dto.status.value,
                },
            )

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

            self.uow.commit()

            logger.info(
    "Document application mis à jour",
    extra={
        "application_id": application.id,
        "document_id": document.id,
        "admin_id": current_admin.id,
    }
)
            return UpdateDocumentResponseDTO(
                document_id=document.id,
                status=document.status,
                comment=document.comment,
            )
        
        except Exception:

            self.uow.rollback()

            logger.exception(
    "Erreur lors de la mise à jour d'un document",
    extra={
        "application_id": application.id,
        "document_id": document.id
    }
)
            raise