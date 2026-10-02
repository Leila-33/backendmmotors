from dataclasses import replace

from core.pagination.paginated_result import PaginatedResult
from modules.vehicles.domain.enums import VehicleStatus

class BaseGetVehiclesUseCase:
    """
    Fournit le traitement commun de recherche et de pagination
    des véhicules pour les différents périmètres d'accès.
    """
    def __init__(self, repo):
        self.repo = repo

    def _execute(self, filters) -> PaginatedResult:

        vehicles, total = self.repo.search(filters)

        return PaginatedResult.create(
            items=vehicles,
            total=total,
            page=filters.page,
            limit=filters.size,
        )


class GetVehiclesForClientUseCase(
    BaseGetVehiclesUseCase
):
    """
    Récupère les véhicules accessibles au client en limitant
    les résultats aux véhicules actuellement disponibles.
    """
    def execute(self, filters) -> PaginatedResult:

        client_filters = replace(
            filters,
            is_available=True,
            status=VehicleStatus.PUBLISHED,
        )

        return self._execute(
            client_filters
        )


class GetVehiclesForAdminUseCase(
    BaseGetVehiclesUseCase
):
    """
    Récupère les véhicules accessibles à l'administration
    selon les critères de recherche, de filtrage et de pagination.
    """
    def execute(self, filters) -> PaginatedResult:

        return self._execute(
            filters
        )