from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.test_drives.infrastructure.db.test_drive_model import TestDriveModel
from modules.test_drives.api.schemas import TestDriveResponse
from modules.test_drives.api.schemas import (
    TestDriveDetailResponse,
    MyTestDriveResponse
)
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

    @staticmethod
    def to_customer_response(model):

        return MyTestDriveResponse(

            id=model.id,

            vehicle_id=model.vehicle_id,

            vehicle_name=(
                f"{model.vehicle.brand} {model.vehicle.model}"
                if model.vehicle
                else ""
            ),

            appointment_date=model.appointment_date,

            status=model.status,

            comment=model.comment,
            created_at=model.created_at,
        )

    @staticmethod
    def to_detail_response(
        test_drive,
        events=None,
    ) -> TestDriveDetailResponse:

        events = events or test_drive.events or []

        return TestDriveDetailResponse(

            # =========================
            # TEST DRIVE
            # =========================

            id=test_drive.id,

            appointment_date=test_drive.appointment_date,

            status=(
                test_drive.status.value
                if hasattr(test_drive.status, "value")
                else test_drive.status
            ),

            comment=test_drive.comment,

            # =========================
            # USER
            # =========================

            user={
                "id": test_drive.user.id,
                "name": (
                    f"{test_drive.user.first_name} "
                    f"{test_drive.user.last_name}"
                ),
                "email": test_drive.user.email,
            },

            # =========================
            # VEHICLE
            # =========================

            vehicle={
                "id": test_drive.vehicle.id,
                "brand": test_drive.vehicle.brand,
                "model": test_drive.vehicle.model,
                "images": test_drive.vehicle.images or [],
                "price": test_drive.vehicle.price,
                "license_plate": (
                    test_drive.vehicle.license_plate
                ),
            },

            # =========================
            # TIMELINE
            # =========================

            timeline=[
                {
                    "id": event.id,
                    "type": (
                        event.type.value
                        if hasattr(event.type, "value")
                        else event.type
                    ),
                    "message": event.message,
                    "date": event.created_at,
                    "metadata": event.event_metadata,
                }
                for event in events
            ],
        )