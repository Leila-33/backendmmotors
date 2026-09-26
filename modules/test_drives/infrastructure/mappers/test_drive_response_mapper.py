from modules.test_drives.api.schemas import (
    MyTestDriveResponse,
    TestDriveDetailResponse,
    TestDriveResponse,
    TestDriveTimelineItem,
    TestDriveUserResponse,
    TestDriveVehicleResponse,
)
from modules.test_drives.domain.entities.test_drive import TestDrive
from modules.vehicles.infrastructure.mappers.vehicle_response_mapper import (
    VehicleResponseMapper,
)


class TestDriveResponseMapper:

    def __init__(
        self,
        vehicle_response_mapper: VehicleResponseMapper,
    ):
        self.vehicle_response_mapper = (
            vehicle_response_mapper
        )

    # ==========================================================
    # TEST DRIVE RESPONSE
    # ==========================================================

    @staticmethod
    def to_response(
        test_drive: TestDrive,
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

    # ==========================================================
    # CUSTOMER RESPONSE
    # ==========================================================

    @staticmethod
    def to_customer_response(
        model,
    ) -> MyTestDriveResponse:

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

    # ==========================================================
    # DETAIL RESPONSE
    # ==========================================================

    def to_detail_response(
        self,
        test_drive,
        events=None,
    ) -> TestDriveDetailResponse:

        events = events or test_drive.events or []

        return TestDriveDetailResponse(

            # ==================================================
            # TEST DRIVE
            # ==================================================

            id=test_drive.id,

            appointment_date=test_drive.appointment_date,

            status=(
                test_drive.status.value
                if hasattr(test_drive.status, "value")
                else test_drive.status
            ),

            comment=test_drive.comment,

            # ==================================================
            # USER
            # ==================================================

            user=TestDriveUserResponse(
                id=test_drive.user.id,
                name=(
                    f"{test_drive.user.first_name} "
                    f"{test_drive.user.last_name}"
                ),
                email=test_drive.user.email,
            ),

            # ==================================================
            # VEHICLE
            # ==================================================

            vehicle=TestDriveVehicleResponse(
                id=test_drive.vehicle.id,
                brand=test_drive.vehicle.brand,
                model=test_drive.vehicle.model,
                images=self.vehicle_response_mapper.map_images(
                    test_drive.vehicle.images
                ),
                price=test_drive.vehicle.price,
                license_plate=(
                    test_drive.vehicle.license_plate
                ),
            ),

            # ==================================================
            # TIMELINE
            # ==================================================

            timeline=[
                TestDriveTimelineItem(
                    id=event.id,
                    type=(
                        event.type.value
                        if hasattr(event.type, "value")
                        else event.type
                    ),
                    message=event.message,
                    date=event.created_at,
                    metadata=event.event_metadata,
                )
                for event in events
            ],
        )