from uuid import uuid4
from datetime import datetime, timezone
from modules.applications.domain.entities.event import Event
from modules.applications.domain.repositories.event_repository import EventRepository
from modules.applications.api.schemas import (
    UpdateApplicationStatusDTO,
    UpdateApplicationStatusResponseDTO,
)
from modules.applications.domain.entities.event import Event
from modules.notifications.domain.enums import (
    NotificationEntityType,
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

from core.database.unit_of_work import UnitOfWork


class UpdateApplicationStatusUseCase:

    def __init__(
        self,
        application_repository,
        notification_service,
        event_repository,
        uow: UnitOfWork,
    ):

        self.application_repository = application_repository
        self.notification_service = notification_service
        self.event_repository = event_repository
        self.uow = uow


    async def execute(
        self,
        application_id: str,
        dto: UpdateApplicationStatusDTO,
    ):

        # =========================
        # GET APPLICATION
        # =========================

        application = (
            self.application_repository.get_by_id(
                application_id
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

        event = Event(

            id=str(uuid4()),

            application_id=application.id,

            type=APPLICATION_EVENT_MAP.get(
                dto.status
            ),

            message=notification.message,

            user_id=application.user_id,

            event_metadata={

                "old_status": (
                    old_status.value
                    if old_status
                    else None
                ),

                "new_status": dto.status.value,

                "reason": dto.reason,
            },

            created_at=datetime.now(
                timezone.utc
            ),
        )


        self.event_repository.save(
            event
        )


        # =========================
        # COMMIT
        # =========================

        self.uow.commit()


        # =========================
        # RESPONSE
        # =========================

        return UpdateApplicationStatusResponseDTO(

            application_id=application.id,

            status=application.status.value,

            message=notification.message,
        )