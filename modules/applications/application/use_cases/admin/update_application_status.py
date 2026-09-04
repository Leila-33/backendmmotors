from core.database.unit_of_work import UnitOfWork

from modules.applications.application.dtos.admin.update_application_status_dto import (
    UpdateApplicationStatusDTO,
)
from modules.applications.application.results.admin.update_application_status_result import (
    UpdateApplicationStatusResult,
)

from modules.applications.domain.application_messages import (
    APPLICATION_EVENT_MAP,
)
from modules.applications.domain.builders.application_notification_builder import (
    ApplicationNotificationBuilder,
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)
from modules.applications.application.dtos.application_id_dto import ApplicationIdDTO

from modules.auth.domain.entities.user import (
    User,
)
from modules.notifications.domain.enums import (
    NotificationEntityType,
)

import logging

logger = logging.getLogger(__name__)

class UpdateApplicationStatusUseCase:

    def __init__(
        self,
        application_repository,
        notification_service,
        event_service,
        uow: UnitOfWork,
    ):

        self.application_repository = application_repository
        self.notification_service = notification_service
        self.event_service = event_service
        self.uow = uow


    async def execute(
        self,
        dto: UpdateApplicationStatusDTO,
        current_admin: User
    ):

        # =========================
        # GET APPLICATION
        # =========================
        try:
            application = (
                self.application_repository.get_by_id(
                    dto.application_id
                )
            )

            if not application:
                raise ApplicationNotFound()


            old_status = application.status


            # =========================
            # UPDATE STATUS
            # =========================

            application.change_status(
                dto.status
            )

            self.application_repository.update(
                application
            )


            # =========================
            # GET USER
            # =========================

            user = application.user


            user_first_name = user.first_name


            # =========================
            # NOTIFICATION
            # =========================

            notification = (
                ApplicationNotificationBuilder.build(
                    application=application,
                    status=dto.status,
                    reason=dto.reason,
                    user_first_name=user_first_name,
                )
            )


            await self.notification_service.send(

                user_id=application.user_id,

                email=user.email,

                entity_type=NotificationEntityType.APPLICATION,

                entity_id=application.id,

                title=notification.title,

                message=notification.message,

                notif_type=notification.type,
            )


            # =========================
            # EVENT
            # =========================

            self.event_service.log(

                application_id=application.id,
                vehicle_id=application.vehicle_id,

                type=APPLICATION_EVENT_MAP.get(
                    dto.status
                ),

                message=notification.message,

                user_id=current_admin.id,

                event_metadata={

                    "old_status": (
                        old_status.value
                        if old_status
                        else None
                    ),

                    "new_status": dto.status.value,

                    "reason": dto.reason,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.uow.commit()

            logger.info(
    "Statut application modifié",
    extra={
        "application_id": application.id,
        "old_status": old_status.value,
        "new_status": application.status.value,
        "admin_id": current_admin.id,
    }
)
            # =========================
            # RESPONSE
            # =========================

            return UpdateApplicationStatusResult(
    id=application.id,
    status=application.status,
)

        except Exception:

            self.uow.rollback()

            logger.exception(
    "Erreur lors de la mise à jour du statut application",
    extra={
        "application_id": dto.application_id,
        "new_status":  dto.status.value
    }
)
     
            raise