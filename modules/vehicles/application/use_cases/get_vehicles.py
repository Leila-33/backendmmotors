from dataclasses import replace

from core.pagination.paginated_result import PaginatedResult


class BaseGetVehiclesUseCase:

    def __init__(self, repo):
        self.repo = repo

    def _execute(self, filters) -> PaginatedResult:

        vehicles, total = self.repo.search(filters)

        return PaginatedResult(
            items=vehicles,
            total=total,
            page=filters.page,
            limit=filters.size,
        )


class GetVehiclesForClientUseCase(
    BaseGetVehiclesUseCase
):

    def execute(self, filters) -> PaginatedResult:

        client_filters = replace(
            filters,
            is_available=True,
        )

        return self._execute(
            client_filters
        )


class GetVehiclesForAdminUseCase(
    BaseGetVehiclesUseCase
):

    def execute(self, filters) -> PaginatedResult:

        return self._execute(
            filters
        )