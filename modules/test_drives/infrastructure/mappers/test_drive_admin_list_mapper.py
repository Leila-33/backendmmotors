from modules.test_drives.api.schemas import (
    PaginatedTestDriveAdminResponse,
    TestDriveAdminItemResponse,
    TestDriveAdminStatsResponse
)
from modules.test_drives.application.results.admin.get_test_drives_admin_result import GetTestDrivesAdminResult
class TestDriveAdminListMapper:

    @staticmethod
    def to_response(test_drive) -> TestDriveAdminItemResponse:

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
    def to_paginated_response(
        result: GetTestDrivesAdminResult,
    ) -> PaginatedTestDriveAdminResponse:

        return PaginatedTestDriveAdminResponse(
            # =========================
            # TEST DRIVES
            # =========================

            items=[
                TestDriveAdminListMapper.to_response(
                    test_drive
                )
                for test_drive in result.pagination.items
            ],

            # =========================
            # PAGINATION
            # =========================

            total=result.pagination.total,
            page=result.pagination.page,
            limit=result.pagination.limit,

            # =========================
            # STATISTIQUES
            # =========================

            stats=TestDriveAdminStatsResponse(
                pending=result.stats.pending,
                confirmed=result.stats.confirmed,
                completed=result.stats.completed,
                cancelled=result.stats.cancelled,
            ),
        )