from datetime import datetime, timezone
from uuid import uuid4
import logging

from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.exceptions import (
    TestDriveSlotUnavailable,
    TestDrivePastDate,
)

from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotAvailableForTestDrive,
)
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType
)
from modules.applications.domain.enums import EventType
from modules.auth.domain.enums import UserRole



logger = logging.getLogger(__name__)


class CreateTestDriveUseCase:

    def __init__(
        self,
        user_repository,
        test_drive_repository,
        vehicle_repository,
        event_service,
        notification_service,
        unit_of_work,
        websocket_manager=None,

    ):
        self.user_repository = user_repository
        self.test_drive_repository = test_drive_repository
        self.vehicle_repository = vehicle_repository
        self.event_service = event_service
        self.notification_service = notification_service
        self.unit_of_work = unit_of_work
        self.websocket_manager = websocket_manager

    async def execute(
        self,
        dto,
        user_id: str,
    ) -> TestDrive:

        try:

            # =========================
            # VEHICLE
            # =========================

            vehicle = (
                self.vehicle_repository.get_by_id(
                    dto.vehicle_id
                )
            )

            if vehicle is None:
                raise VehicleNotFound()

            if vehicle.status != VehicleStatus.PUBLISHED:
                raise VehicleNotAvailableForTestDrive()

            # =========================
            # DATE
            # =========================

            if dto.appointment_date <= datetime.now(timezone.utc):
                raise TestDrivePastDate()

            # =========================
            # SLOT
            # =========================

            existing = (
                self.test_drive_repository
                .find_conflicting_slot(
                    vehicle_id=dto.vehicle_id,
                    appointment_date=dto.appointment_date,
                )
            )

            if existing:
                raise TestDriveSlotUnavailable()

            # =========================
            # CREATE
            # =========================

            test_drive = TestDrive(
                id=str(uuid4()),
                user_id=user_id,
                vehicle_id=dto.vehicle_id,
                appointment_date=dto.appointment_date,
                status=TestDriveStatus.PENDING,
                comment=dto.comment,
                created_at=datetime.now(timezone.utc),
            )

            self.test_drive_repository.create(
                test_drive
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.TEST_DRIVE_CREATED,
                message="Demande d'essai véhicule créée",
                user_id=user_id,
                vehicle_id=vehicle.id,
                test_drive_id=test_drive.id,
                event_metadata={
                    "appointment_date":
                        test_drive.appointment_date.isoformat(),

                    "status":
                        test_drive.status.value,
                },
            )

            # =========================
            # NOTIFICATION
            # =========================
            admins = self.user_repository.get_by_role(UserRole.ADMIN)

            for admin in admins:
                await self.notification_service.send(
                    user_id=admin.id,

                    title="Nouvel essai routier",

                    message="Un client a demandé un essai routier.",

                    notif_type=NotificationType.TEST_DRIVE_CREATED,

                    entity_type=NotificationEntityType.TEST_DRIVE,

                    entity_id=test_drive.id,
                )
            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            pending_count = (
                self.test_drive_repository.count_pending()
            )

            for admin in admins:
                await self.websocket_manager.send(
                    str(admin.id),
                    {
                        "type": "TEST_DRIVE_PENDING_UPDATED",
                        "count": pending_count,
                    },
                )

            logger.info(
                "Demande d'essai routier créée",
                extra={
                    "test_drive_id": test_drive.id,
                    "user_id": user_id,
                    "vehicle_id": test_drive.vehicle_id,
                },
            )

            return test_drive

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création essai routier",
                extra={
                    "user_id": user_id,
                    "vehicle_id": dto.vehicle_id,
                },
            )

            raise