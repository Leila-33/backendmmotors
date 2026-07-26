from modules.test_drives.api.schemas import (
    TestDriveAdminListItemResponse,
    TestDriveAdminListResponse
)

class TestDriveAdminListMapper:

    @staticmethod
    def to_item(test_drive) -> TestDriveAdminListItemResponse:

        return TestDriveAdminListItemResponse(
            id=test_drive.id,

            user_name=(
                f"{test_drive.user.first_name} "
                f"{test_drive.user.last_name}"
            ),

            vehicle_name=(
                f"{test_drive.vehicle.brand} "
                f"{test_drive.vehicle.model}"
            ),

            appointment_date=test_drive.appointment_date,

            status=test_drive.status.value
        )


    @staticmethod
    def to_response(result):

        return TestDriveAdminListResponse(
            items=[
                TestDriveAdminListMapper.to_item(td)
                for td in result.items
            ],
            total=result.total,
            page=result.page,
            limit=result.limit
        )