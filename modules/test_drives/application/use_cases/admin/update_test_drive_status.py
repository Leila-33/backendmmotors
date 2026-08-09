from modules.test_drives.domain.exceptions import TestDriveNotFound, TestDriveStatusForbidden
from modules.applications.domain.enums import EventType
from modules.test_drives.domain.enums import TestDriveStatus
from modules.notifications.domain.enums import NotificationType, NotificationEntityType
from modules.auth.domain.exceptions import Forbidden
from modules.auth.domain.enums import UserRole
from modules.test_drives.domain.test_drive_messages import (
    TEST_DRIVE_EVENT_MAP,
    TEST_DRIVE_STATUS_LABELS
)
import logging


logger = logging.getLogger(__name__)




class UpdateTestDriveStatusUseCase:

    def __init__(
        self,
        repository,
        event_service,
        unit_of_work,
        notification_service=None,
    ):
        self.repository = repository
        self.event_service = event_service
        self.uow = unit_of_work
        self.notification_service = notification_service


    async def execute(
        self,
        test_drive_id: str,
        status: TestDriveStatus,
        actor_id: str,
        actor_role: str
    ):


        # =========================
        # LOAD
        # =========================

        test_drive = (
            self.repository
            .get_full_by_id(test_drive_id)
        )


        if not test_drive:
            raise TestDriveNotFound()



        # =========================
        # SECURITY
        # =========================

        if actor_role == UserRole.CLIENT:

            if test_drive.user_id != actor_id:
                raise Forbidden()


            if status != TestDriveStatus.CANCELLED:
                raise TestDriveStatusForbidden()


        if test_drive.status == status:
            return test_drive

        old_status = test_drive.status



        try:

            # =========================
            # UPDATE STATUS
            # =========================

            test_drive.status = status

            self.repository.update(test_drive)



            # =========================
            # EVENT
            # =========================
            event_type = TEST_DRIVE_EVENT_MAP.get(status)
            
            if event_type:

                self.event_service.log(

                    test_drive_id=test_drive.id,

                    type=event_type,

                    message=(
                        f"Statut de l'essai routier changé vers "
                        f"{TEST_DRIVE_STATUS_LABELS[status]}"
                    ),

                    user_id=actor_id,
                    event_metadata={
                        "customer_id": test_drive.user_id,

                        "old_status":
                            old_status.value
                            if old_status
                            else None,

                        "new_status":
                            status.value
                    },
                )
            # =========================
            # COMMIT TRANSACTION
            # =========================

            self.uow.commit()

            logger.info(
    "Statut essai routier modifié",
    extra={
        "test_drive_id": test_drive.id,
        "actor_id": actor_id,
        "old_status": old_status.value,
        "new_status": status.value,
    },
)
            if (
                self.notification_service
                and test_drive.user
            ):


                notif = self._build_notification(
                    status,
                    test_drive
                )


                await self.notification_service.send(

                    user_id=test_drive.user_id,

                    email=test_drive.user.email,

                    entity_type=
                        NotificationEntityType.TEST_DRIVE,

                    entity_id=test_drive.id,

                    title=notif["title"],

                    message=notif["message"],

                    notif_type=notif["type"]
                )

            return test_drive

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur modification statut essai routier",
                extra={
                    "test_drive_id": test_drive_id,
                    "actor_id": actor_id,
                    "new_status": status.value,
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