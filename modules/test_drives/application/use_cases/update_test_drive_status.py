import logging

from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.domain.exceptions import (
    TestDriveNotFound,
    TestDriveStatusForbidden,
)
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.test_drive_messages import (
    TEST_DRIVE_EVENT_MAP,
    TEST_DRIVE_STATUS_LABELS,
)
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType
)

from modules.auth.domain.exceptions import Forbidden
from modules.auth.domain.enums import UserRole

from modules.test_drives.application.dtos.update_test_drive_status_dto import (
    UpdateTestDriveStatusDTO,
)



logger = logging.getLogger(__name__)


class UpdateTestDriveStatusUseCase:

    def __init__(
        self,
        repository,
        user_repository,
        event_service,
        unit_of_work,
        notification_service=None,
        websocket_manager=None,
    ):
        self.repository = repository
        self.user_repository = user_repository
        self.event_service = event_service
        self.uow = unit_of_work
        self.notification_service = notification_service
        self.websocket_manager = websocket_manager


    async def execute(
        self,
        dto: UpdateTestDriveStatusDTO,
    ) -> TestDrive:

        # =========================
        # LOAD
        # =========================

        test_drive = self.repository.get_full_by_id(
            dto.test_drive_id
        )

        if test_drive is None:
            raise TestDriveNotFound()

        # =========================
        # SECURITY
        # =========================

        if dto.actor_role == UserRole.CLIENT:

            if test_drive.user_id != dto.actor_id:
                raise Forbidden()

            if dto.status != TestDriveStatus.CANCELLED:
                raise TestDriveStatusForbidden()

        # =========================
        # NO CHANGE
        # =========================

        if test_drive.status == dto.status:

            return test_drive

        old_status = test_drive.status

        try:

            # =========================
            # UPDATE STATUS
            # =========================

            test_drive.status = dto.status

            updated_test_drive = (
                self.repository.update(
                    test_drive
                )
            )

            # =========================
            # EVENT
            # =========================

            event_type = TEST_DRIVE_EVENT_MAP.get(
                dto.status
            )

            if event_type:

                self.event_service.log(

                    test_drive_id=updated_test_drive.id,

                    type=event_type,

                    message=(
                        "Statut de l'essai routier changé vers "
                        f"{TEST_DRIVE_STATUS_LABELS[dto.status]}"
                    ),

                    vehicle_id=updated_test_drive.vehicle_id,

                    user_id=dto.actor_id,

                    event_metadata={

                        "customer_id":
                            updated_test_drive.user_id,

                        "old_status":
                            old_status.value,

                        "new_status":
                            dto.status.value,
                    },
                )


            # =========================
            # NOTIFICATION
            # =========================

            if (
                self.notification_service
                and updated_test_drive.user
            ):

                notif = self._build_notification(
                    dto.status,
                    updated_test_drive,
                )

                await self.notification_service.send(

                    user_id=updated_test_drive.user_id,

                    email=updated_test_drive.user.email,

                    entity_type=(
                        NotificationEntityType.TEST_DRIVE
                    ),

                    entity_id=updated_test_drive.id,

                    title=notif["title"],

                    message=notif["message"],

                    notif_type=notif["type"],
                )

            # =========================
            # COMMIT
            # =========================

            self.uow.commit()

            if self.websocket_manager:
            
                await self._notify_admin_test_drive_count()

            logger.info(
                "Statut essai routier modifié",
                extra={
                    "test_drive_id":
                        updated_test_drive.id,

                    "actor_id":
                        dto.actor_id,

                    "old_status":
                        old_status.value,

                    "new_status":
                        dto.status.value,
                },
            )
            
            return test_drive
        
        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur modification statut essai routier",
                extra={
                    "test_drive_id":
                        dto.test_drive_id,

                    "actor_id":
                        dto.actor_id,

                    "new_status":
                        dto.status.value,
                },
            )

            raise



    def _build_notification(self, status, test_drive):

        appointment_date = test_drive.appointment_date

        formatted_date = (
            appointment_date.strftime("%d/%m/%Y à %H:%M")
            if appointment_date else "date non définie"
        )

        vehicle_name = (
            f"{test_drive.vehicle.brand} {test_drive.vehicle.model}"
            if test_drive.vehicle else "véhicule non défini"
        )
        if status == TestDriveStatus.CONFIRMED:
            return {
                "title": "Essai routier confirmé",
                "type": NotificationType.TEST_DRIVE_CONFIRMED,
                "message": (
                    f"Bonjour,\n\n"
                    f"Votre essai routier du {formatted_date} "
                    f"avec le véhicule {vehicle_name} a été confirmé.\n\n"
                    f"Nous vous attendons à la date convenue.\n\n"
                    f"Cordialement,\nL’équipe Mmotors"
                )
            }
        if status == TestDriveStatus.REJECTED:
            return {
                "title": "Essai routier refusé",
                "type": NotificationType.TEST_DRIVE_REJECTED,
                "message": (
                    f"Bonjour,\n\n"
                    f"Votre essai routier du {formatted_date} "
                    f"avec le véhicule {vehicle_name} a été refusé.\n\n"
                    f"Vous pouvez choisir un autre créneau.\n\n"
                    f"Cordialement,\nL’équipe Mmotors"
                )
            }
        if status == TestDriveStatus.CANCELLED:
            return {
                "title": "Essai routier annulé",
                "type": NotificationType.TEST_DRIVE_CANCELLED,
                "message": (
                    f"Bonjour,\n\n"
                    f"Votre essai routier du {formatted_date} a été annulé.\n\n"
                    f"Cordialement,\nL’équipe Mmotors"
                )
            }
        
        if status == TestDriveStatus.COMPLETED:
            return {
                "title": "Essai routier terminé",
                "type": NotificationType.TEST_DRIVE_COMPLETED,
                "message": (
                    f"Bonjour,\n\n"
                    f"Merci d’avoir effectué votre essai du {formatted_date} "
                    f"avec le véhicule {vehicle_name}.\n\n"
                    f"N’hésitez pas à nous recontacter.\n\n"
                    f"Cordialement,\nL’équipe Mmotors"
                )
            }

    async def _notify_admin_test_drive_count(self):

        pending_count = self.repository.count_pending()

        admins = self.user_repository.get_by_role(
            UserRole.ADMIN
        )
        for admin in admins:
            await self.websocket_manager.send(
                str(admin.id),
                {
                    "type": "TEST_DRIVE_PENDING_UPDATED",
                    "count": pending_count,
                },
            )