from dataclasses import replace
from unittest.mock import MagicMock

from modules.vehicles.application.use_cases.get_vehicles import (
    GetVehiclesForAdminUseCase,
    GetVehiclesForClientUseCase,
)
from modules.vehicles.application.dtos.vehicle_search_filters_dto import (
    VehicleSearchFiltersDTO,
)
from modules.vehicles.domain.enums import (
    VehicleStatus,
)


class TestGetVehiclesForClientUseCase:
    """Tests du Use Case de récupération des véhicules côté client."""

    def test_execute_forces_available_and_published_filters(self):
        # Arrange
        repo = MagicMock()

        vehicles = [
            MagicMock(),
            MagicMock(),
        ]

        repo.search.return_value = (vehicles, 2)

        filters = VehicleSearchFiltersDTO(
            page=2,
            size=5,
            sort_by="price",
            order="asc",
            brand="Peugeot",
            model="308",
            is_available=False,
            status=VehicleStatus.ARCHIVED,
        )

        use_case = GetVehiclesForClientUseCase(repo)

        # Act
        result = use_case.execute(filters)

        # Assert
        repo.search.assert_called_once()

        called_filters = repo.search.call_args.args[0]

        assert called_filters.is_available is True
        assert called_filters.status == VehicleStatus.PUBLISHED

        # Les autres filtres sont conservés.
        assert called_filters.page == 2
        assert called_filters.size == 5
        assert called_filters.sort_by == "price"
        assert called_filters.order == "asc"
        assert called_filters.brand == "Peugeot"
        assert called_filters.model == "308"

        # Le DTO original n'est pas modifié.
        assert filters.is_available is False
        assert filters.status == VehicleStatus.ARCHIVED

    def test_execute_preserves_client_filters(self):
        # Arrange
        repo = MagicMock()
        repo.search.return_value = ([], 0)

        filters = VehicleSearchFiltersDTO(
            page=1,
            size=10,
            sort_by="year",
            order="desc",
            type=None,
            brand="Renault",
            model="Clio",
            engine_type=None,
            price_min=5000,
            price_max=15000,
            year_min=2018,
            mileage_max=100000,
        )

        use_case = GetVehiclesForClientUseCase(repo)

        # Act
        use_case.execute(filters)

        # Assert
        called_filters = repo.search.call_args.args[0]

        assert called_filters.brand == "Renault"
        assert called_filters.model == "Clio"
        assert called_filters.price_min == 5000
        assert called_filters.price_max == 15000
        assert called_filters.year_min == 2018
        assert called_filters.mileage_max == 100000

        assert called_filters.page == 1
        assert called_filters.size == 10
        assert called_filters.sort_by == "year"
        assert called_filters.order == "desc"

    def test_execute_returns_paginated_result(self):
        # Arrange
        repo = MagicMock()

        vehicles = [
            MagicMock(),
            MagicMock(),
        ]

        repo.search.return_value = (vehicles, 25)

        filters = VehicleSearchFiltersDTO(
            page=2,
            size=10,
        )

        use_case = GetVehiclesForClientUseCase(repo)

        # Act
        result = use_case.execute(filters)

        # Assert
        assert result.items == vehicles
        assert result.total == 25
        assert result.page == 2
        assert result.limit == 10


class TestGetVehiclesForAdminUseCase:
    """Tests du Use Case de récupération des véhicules côté administration."""

    def test_execute_passes_filters_unchanged(self):
        # Arrange
        repo = MagicMock()
        repo.search.return_value = ([], 0)

        filters = VehicleSearchFiltersDTO(
            page=3,
            size=20,
            sort_by="mileage",
            order="asc",
            type=None,
            brand="BMW",
            model="X3",
            search="BMW X3",
            license_plate="AB-123-CD",
            is_available=False,
            status=VehicleStatus.ARCHIVED,
        )

        use_case = GetVehiclesForAdminUseCase(repo)

        # Act
        use_case.execute(filters)

        # Assert
        repo.search.assert_called_once_with(filters)

    def test_execute_returns_paginated_result(self):
        # Arrange
        repo = MagicMock()

        vehicles = [
            MagicMock(),
            MagicMock(),
            MagicMock(),
        ]

        repo.search.return_value = (vehicles, 53)

        filters = VehicleSearchFiltersDTO(
            page=2,
            size=10,
        )

        use_case = GetVehiclesForAdminUseCase(repo)

        # Act
        result = use_case.execute(filters)

        # Assert
        assert result.items == vehicles
        assert result.total == 53
        assert result.page == 2
        assert result.limit == 10

    def test_execute_keeps_admin_specific_filters(self):
        # Arrange
        repo = MagicMock()
        repo.search.return_value = ([], 0)

        filters = VehicleSearchFiltersDTO(
            page=1,
            size=10,
            search="Peugeot",
            license_plate="AA-123-AA",
            status=VehicleStatus.ARCHIVED,
            is_available=False,
        )

        use_case = GetVehiclesForAdminUseCase(repo)

        # Act
        use_case.execute(filters)

        # Assert
        repo.search.assert_called_once_with(filters)

        called_filters = repo.search.call_args.args[0]

        assert called_filters.search == "Peugeot"
        assert called_filters.license_plate == "AA-123-AA"
        assert called_filters.status == VehicleStatus.ARCHIVED
        assert called_filters.is_available is False