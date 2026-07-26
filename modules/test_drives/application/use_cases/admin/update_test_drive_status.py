from datetime import datetime, timezone
from modules.test_drives.domain.exceptions import TestDriveNotFound, TestDriveStatusForbidden
from modules.applications.domain.entities.event import Event
from modules.applications.domain.enums import EventType
from modules.test_drives.domain.enums import TestDriveStatus
from modules.notifications.domain.enums import NotificationType, NotificationEntityType
from uuid import uuid4
from modules.auth.domain.exceptions import Forbidden




class UpdateTestDriveStatusUseCase:

    def __init__(
        self,
        repository,
        event_repository,
        unit_of_work,
        notification_service=None
    ):
        self.repository = repository
        self.event_repository = event_repository
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

        if actor_role == "client":

            if test_drive.user_id != actor_id:
                raise Forbidden()


            if status != TestDriveStatus.CANCELLED:
                raise TestDriveStatusForbidden()



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

            event = Event(

                id=str(uuid4()),

                test_drive_id=test_drive.id,

                type=self._map_status_to_event(status),

                message=(
                    "Statut de l’essai routier changé vers "
                f"{self._translate_status(status)}"
                ),

                user_id=test_drive.user_id,

                event_metadata={

                    "old_status":
                        old_status.value
                        if old_status
                        else None,

                    "new_status":
                        status.value
                },


                created_at=datetime.now(timezone.utc)
            )


            self.event_repository.save(event)


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

            # =========================
            # COMMIT TRANSACTION
            # =========================

            self.uow.commit()



        except Exception:

            self.uow.rollback()

            raise

        return test_drive




    # =========================
    # EVENT MAPPING
    # =========================

    def _map_status_to_event(
        self,
        status: TestDriveStatus
    ):

        mapping = {

            TestDriveStatus.CONFIRMED:
                EventType.TEST_DRIVE_CONFIRMED,


            TestDriveStatus.REJECTED:
                EventType.TEST_DRIVE_REJECTED,


            TestDriveStatus.CANCELLED:
                EventType.TEST_DRIVE_CANCELLED,


            TestDriveStatus.COMPLETED:
                EventType.TEST_DRIVE_COMPLETED,
        }


        return mapping.get(status)

    def _translate_status(self, status: TestDriveStatus):

        translations = {

            TestDriveStatus.PENDING:
                "En attente",

            TestDriveStatus.CONFIRMED:
                "Confirmé",

            TestDriveStatus.REJECTED:
                "Refusé",

            TestDriveStatus.CANCELLED:
                "Annulé",

            TestDriveStatus.COMPLETED:
                "Terminé",

        }

        return translations.get(
            status,
            status.value
        )

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