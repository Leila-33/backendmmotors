from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.infrastructure.db.test_drive_model import TestDriveModel
from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper
from modules.auth.infrastructure.mappers.user_mapper import UserMapper

class TestDriveMapper:


    @staticmethod
    def to_domain(
        model: TestDriveModel
    ) -> TestDrive:

        return TestDrive(
            id=model.id,
            user_id=model.user_id,
            vehicle_id=model.vehicle_id,
            vehicle=(
            VehicleMapper.to_domain(model.vehicle)
            if model.vehicle
            else None
        ),
            user=(
            UserMapper.to_domain(model.user)
            if model.user
            else None
        ),
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




