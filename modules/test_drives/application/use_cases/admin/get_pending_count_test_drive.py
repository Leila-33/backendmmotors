from modules.test_drives.application.results.admin.get_pending_test_drive_count_result import (
    GetPendingTestDriveCountResult,
)


class GetPendingTestDriveCountUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self) -> GetPendingTestDriveCountResult:

        count = self.repository.count_pending()

        return GetPendingTestDriveCountResult(
            count=count
        )