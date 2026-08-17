from modules.test_drives.application.dtos.admin.get_test_drives_admin_dto import (
    GetTestDrivesAdminDTO,
)
from core.pagination.paginated_result import (
    PaginatedResult,
)


class GetTestDrivesAdminUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(
        self,
        dto: GetTestDrivesAdminDTO,
    ) -> PaginatedResult:

        return self.repository.get_all_admin(
            status=dto.status,
            search=dto.search,
            page=dto.page,
            limit=dto.limit,
        )