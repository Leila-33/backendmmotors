from uuid import uuid4
from datetime import datetime, timezone
from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.domain.enums import TestDriveStatus
from modules.test_drives.domain.exceptions import TestDriveSlotUnavailable, TestDrivePastDate
from modules.test_drives.domain.entities.test_drive import (
    TestDrive,
)
from modules.test_drives.domain.enums import TestDriveStatus
from modules.vehicles.domain.enums import VehicleStatus
from modules.test_drives.domain.exceptions import (
    TestDriveSlotUnavailable,
    TestDrivePastDate
)
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotAvailableForTestDrive,
)
from modules.applications.domain.enums import EventType
import logging


logger = logging.getLogger(__name__)

class CreateTestDriveUseCase:

    def __init__(
        self,
        test_drive_repository,
        vehicle_repository,
        event_service,
        unit_of_work,
    ):
        self.test_drive_repository = test_drive_repository
        self.vehicle_repository = vehicle_repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto,
        current_user,
    ):
        try:
            # =========================
            # VEHICLE
            # =========================
            vehicle = (
                self.vehicle_repository
                .get_by_id(dto.vehicle_id)
            )

            if vehicle is None:
                raise VehicleNotFound()

            if vehicle.status != VehicleStatus.PUBLISHED:
                raise VehicleNotAvailableForTestDrive()

            # =========================
            # PAST DATE
            # =========================
            if dto.appointment_date <= datetime.now(timezone.utc):
                raise TestDrivePastDate()

            # =========================
            # SLOT CONFLICT
            # =========================
            existing = (
                self.test_drive_repository
                .find_conflicting_slot(
                    dto.vehicle_id,
                    dto.appointment_date,
                )
            )

            if existing:
                raise TestDriveSlotUnavailable()

            # =========================
            # CREATE
            # =========================
            test_drive = TestDrive(
                id=str(uuid4()),
                user_id=current_user.id,
                vehicle_id=dto.vehicle_id,
                appointment_date=dto.appointment_date,
                status=TestDriveStatus.PENDING,
                comment=dto.comment,
                created_at=datetime.now(timezone.utc),
            )

            self.test_drive_repository.create(
                test_drive
            )
            self.event_service.log(
        type=EventType.TEST_DRIVE_CREATED,
        message="Demande d'essai véhicule créée",
        user_id=current_user.id,
        vehicle_id=vehicle.id,
        test_drive_id=test_drive.id,
        event_metadata={
            "appointment_date": (
                test_drive.appointment_date.isoformat()
            ),
            "status": test_drive.status.value,
        }
    )
            self.unit_of_work.commit()

            logger.info(
        "Demande d'essai routier créée",
        extra={
            "test_drive_id": test_drive.id,
            "user_id": current_user.id,
            "vehicle_id": test_drive.vehicle_id,
        },
    )
            return test_drive
        
        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création essai routier",
                extra={
                    "user_id": current_user.id,
                    "vehicle_id": dto.vehicle_id,
                },
            )

            raise