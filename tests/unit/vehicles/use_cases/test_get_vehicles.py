from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from core.pagination.paginated_result import PaginatedResult
from modules.vehicles.application.use_cases.get_vehicles import (
    GetVehiclesForAdminUseCase,
    GetVehiclesForClientUseCase,
)


# ============================================================
# TEST FILTERS
# ============================================================
#
# Dataclass volontairement minimale.
# Elle contient les champs utilisés par les use cases :
# - page
# - size
# - is_available
#
# Les autres champs éventuels de ton vrai DTO peuvent être
# ajoutés ici si nécessaire.
# ============================================================


@dataclass(frozen=True)
class TestVehicleFilters:
    page: int = 1
    size: int = 10
    is_available: bool | None = None


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def client_use_case(repository):
    return GetVehiclesForClientUseCase(
        repo=repository,
    )


@pytest.fixture
def admin_use_case(repository):
    return GetVehiclesForAdminUseCase(
        repo=repository,
    )


@pytest.fixture
def filters():
    return TestVehicleFilters(
        page=1,
        size=10,
        is_available=None,
    )


# ============================================================
# HELPERS
# ============================================================


def make_paginated_result(
    *,
    items=None,
    total=0,
    page=1,
    limit=10,
):
    return PaginatedResult(
        items=items or [],
        total=total,
        page=page,
        limit=limit,
    )


# ============================================================
# CLIENT
# ============================================================


def test_client_forces_is_available_to_true(
    client_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        ["vehicle-1", "vehicle-2"],
        2,
    )

    client_use_case.execute(filters)

    passed_filters = repository.search.call_args.args[0]

    assert passed_filters.is_available is True


def test_client_does_not_modify_original_filters(
    client_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        [],
        0,
    )

    client_use_case.execute(filters)

    assert filters.is_available is None


def test_client_preserves_other_filters(
    client_use_case,
    repository,
):
    filters = TestVehicleFilters(
        page=3,
        size=20,
        is_available=False,
    )

    repository.search.return_value = (
        [],
        0,
    )

    client_use_case.execute(filters)

    passed_filters = repository.search.call_args.args[0]

    assert passed_filters.page == 3
    assert passed_filters.size == 20
    assert passed_filters.is_available is True


def test_client_calls_repository_search_once(
    client_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        [],
        0,
    )

    client_use_case.execute(filters)

    repository.search.assert_called_once()


# ============================================================
# ADMIN
# ============================================================


def test_admin_passes_filters_unchanged(
    admin_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        ["vehicle-1"],
        1,
    )

    admin_use_case.execute(filters)

    passed_filters = repository.search.call_args.args[0]

    assert passed_filters is filters


def test_admin_preserves_is_available_filter(
    admin_use_case,
    repository,
):
    filters = TestVehicleFilters(
        page=2,
        size=15,
        is_available=False,
    )

    repository.search.return_value = (
        [],
        0,
    )

    admin_use_case.execute(filters)

    passed_filters = repository.search.call_args.args[0]

    assert passed_filters is filters
    assert passed_filters.is_available is False


def test_admin_calls_repository_search_once(
    admin_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        [],
        0,
    )

    admin_use_case.execute(filters)

    repository.search.assert_called_once_with(filters)


# ============================================================
# PAGINATION
# ============================================================


def test_client_builds_paginated_result(
    client_use_case,
    repository,
):
    filters = TestVehicleFilters(
        page=2,
        size=20,
    )

    vehicles = [
        "vehicle-1",
        "vehicle-2",
    ]

    repository.search.return_value = (
        vehicles,
        45,
    )

    result = client_use_case.execute(filters)

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == vehicles
    assert result.total == 45
    assert result.page == 2
    assert result.limit == 20


def test_admin_builds_paginated_result(
    admin_use_case,
    repository,
):
    filters = TestVehicleFilters(
        page=3,
        size=15,
    )

    vehicles = [
        "vehicle-1",
        "vehicle-2",
        "vehicle-3",
    ]

    repository.search.return_value = (
        vehicles,
        38,
    )

    result = admin_use_case.execute(filters)

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == vehicles
    assert result.total == 38
    assert result.page == 3
    assert result.limit == 15


# ============================================================
# EMPTY RESULTS
# ============================================================


def test_client_returns_empty_paginated_result(
    client_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        [],
        0,
    )

    result = client_use_case.execute(filters)

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == []
    assert result.total == 0
    assert result.page == filters.page
    assert result.limit == filters.size


def test_admin_returns_empty_paginated_result(
    admin_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        [],
        0,
    )

    result = admin_use_case.execute(filters)

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == []
    assert result.total == 0


# ============================================================
# DIFFERENT COUNTS
# ============================================================


@pytest.mark.parametrize(
    "total",
    [
        0,
        1,
        10,
        25,
        100,
    ],
)
def test_client_preserves_repository_total(
    total,
    client_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        [],
        total,
    )

    result = client_use_case.execute(filters)

    assert result.total == total


@pytest.mark.parametrize(
    "total",
    [
        0,
        1,
        10,
        25,
        100,
    ],
)
def test_admin_preserves_repository_total(
    total,
    admin_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        [],
        total,
    )

    result = admin_use_case.execute(filters)

    assert result.total == total


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_client_propagates_repository_error(
    client_use_case,
    repository,
    filters,
):
    repository.search.side_effect = RuntimeError(
        "repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        client_use_case.execute(filters)


def test_admin_propagates_repository_error(
    admin_use_case,
    repository,
    filters,
):
    repository.search.side_effect = RuntimeError(
        "repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        admin_use_case.execute(filters)


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_client_does_not_write_to_repository(
    client_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        [],
        0,
    )

    client_use_case.execute(filters)

    repository.create.assert_not_called()
    repository.update.assert_not_called()
    repository.delete.assert_not_called()


def test_admin_does_not_write_to_repository(
    admin_use_case,
    repository,
    filters,
):
    repository.search.return_value = (
        [],
        0,
    )

    admin_use_case.execute(filters)

    repository.create.assert_not_called()
    repository.update.assert_not_called()
    repository.delete.assert_not_called()