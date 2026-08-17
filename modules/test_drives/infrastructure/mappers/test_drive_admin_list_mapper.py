from modules.test_drives.api.schemas import (
    PaginatedTestDriveAdminResponse,
    TestDriveAdminItemResponse
)

class TestDriveAdminListMapper:

    @staticmethod
    def to_item(test_drive) -> TestDriveAdminItemResponse:

        return TestDriveAdminItemResponse(
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

            status=test_drive.status.value,
            comment=test_drive.comment
        )


    @staticmethod
    def to_paginated_response(result):

        return PaginatedTestDriveAdminResponse(
            items=[
                TestDriveAdminListMapper.to_item(td)
                for td in result.items
            ],
            total=result.total,
            page=result.page,
            limit=result.limit
        )