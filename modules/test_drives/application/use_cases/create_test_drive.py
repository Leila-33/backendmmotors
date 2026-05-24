from uuid import uuid4
from datetime import datetime, timezone

from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.core.enums import TestDriveStatus
from modules.core.exceptions import TestDriveSlotUnavailable, TestDrivePastDate

class CreateTestDriveUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, dto, current_user):

        # =========================
        # 1. PAST DATE CHECK
        # =========================
        if dto.appointment_date < datetime.now(timezone.utc):
            raise TestDrivePastDate()

        # =========================
        # 2. SLOT CONFLICT CHECK
        # =========================
        existing = self.repository.find_conflicting_slot(
            dto.vehicle_id,
            dto.appointment_date
        )
        if existing:
            raise TestDriveSlotUnavailable()

        # =========================
        # 3. CREATE
        # =========================
        test_drive = TestDrive(
            id=str(uuid4()),
            user_id=current_user.id,
            vehicle_id=dto.vehicle_id,
            appointment_date=dto.appointment_date,
            status=TestDriveStatus.PENDING,
            comment=dto.comment,
            created_at=datetime.now(timezone.utc)
        )

        self.repository.create(test_drive)
        self.repository.commit()

        return test_drive