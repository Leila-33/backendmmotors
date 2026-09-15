from modules.test_drives.application.dtos.admin.get_test_drives_admin_dto import (
    GetTestDrivesAdminDTO,
)
from modules.test_drives.application.results.admin.get_test_drives_admin_result import (
    GetTestDrivesAdminResult
)


class GetTestDrivesAdminUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(
        self,
        dto: GetTestDrivesAdminDTO,
    ) -> GetTestDrivesAdminResult:

        return self.repository.get_all_admin(
            status=dto.status,
            search=dto.search,
            date=dto.date,
            sort_by=dto.sort_by,
            sort_order=dto.sort_order,
            page=dto.page,
            limit=dto.limit,
        )