from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.infrastructure.db.test_drive_model import TestDriveModel
from modules.test_drives.api.schemas import TestDriveResponse


class TestDriveMapper:


    @staticmethod
    def to_domain(
        model: TestDriveModel
    ) -> TestDrive:

        return TestDrive(
            id=model.id,
            user_id=model.user_id,
            vehicle_id=model.vehicle_id,
            appointment_date=model.appointment_date,
            status=model.status,
            comment=model.comment,
            created_at=model.created_at,
        )


    @staticmethod
    def to_model(
        test_drive: TestDrive
    ) -> TestDriveModel:

        return TestDriveModel(
            id=test_drive.id,
            user_id=test_drive.user_id,
            vehicle_id=test_drive.vehicle_id,
            appointment_date=test_drive.appointment_date,
            status=test_drive.status,
            comment=test_drive.comment,
            created_at=test_drive.created_at,
        )


    @staticmethod
    def update_model(
        model: TestDriveModel,
        test_drive: TestDrive,
    ) -> TestDriveModel:

        model.appointment_date = (
            test_drive.appointment_date
        )

        model.status = (
            test_drive.status
        )

        model.comment = (
            test_drive.comment
        )

        return model


    @staticmethod
    def to_response(
        test_drive: TestDrive
    ) -> TestDriveResponse:

        return TestDriveResponse(
            id=test_drive.id,
            user_id=test_drive.user_id,
            vehicle_id=test_drive.vehicle_id,
            appointment_date=test_drive.appointment_date,
            status=test_drive.status,
            comment=test_drive.comment,
            created_at=test_drive.created_at,
        )