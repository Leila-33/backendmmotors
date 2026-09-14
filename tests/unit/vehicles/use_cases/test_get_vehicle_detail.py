from unittest.mock import Mock

import pytest

from modules.vehicles.application.use_cases.get_vehicle_detail import (
    GetVehicleDetailUseCase,
)
from modules.vehicles.domain.exceptions import VehicleNotFound


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def use_case(vehicle_repository):
    return GetVehicleDetailUseCase(
        vehicle_repository=vehicle_repository,
    )


# ============================================================
# SUCCESS
# ============================================================


def test_execute_returns_vehicle(
    use_case,
    vehicle_repository,
):
    vehicle = Mock(
        id="vehicle-1",
        brand="BMW",
        model="Serie 3",
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(
        vehicle_id="vehicle-1",
    )

    assert result is vehicle


def test_execute_returns_exact_vehicle_data(
    use_case,
    vehicle_repository,
):
    vehicle = Mock(
        id="vehicle-42",
        brand="Audi",
        model="A3",
        price=25000,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(
        vehicle_id="vehicle-42",
    )

    assert result.id == "vehicle-42"
    assert result.brand == "Audi"
    assert result.model == "A3"
    assert result.price == 25000


# ============================================================
# REPOSITORY CALL
# ============================================================


def test_execute_calls_repository_with_vehicle_id(
    use_case,
    vehicle_repository,
):
    vehicle_repository.get_by_id.return_value = Mock(
        id="vehicle-1",
    )

    use_case.execute(
        vehicle_id="vehicle-1",
    )

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-1",
    )


def test_execute_uses_exact_vehicle_id(
    use_case,
    vehicle_repository,
):
    vehicle_repository.get_by_id.return_value = Mock(
        id="vehicle-99",
    )

    use_case.execute(
        vehicle_id="vehicle-99",
    )

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-99",
    )


# ============================================================
# NOT FOUND
# ============================================================


def test_execute_raises_vehicle_not_found(
    use_case,
    vehicle_repository,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(
            vehicle_id="unknown-vehicle",
        )


def test_vehicle_not_found_does_not_perform_other_operations(
    use_case,
    vehicle_repository,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(
            vehicle_id="unknown-vehicle",
        )

    vehicle_repository.create.assert_not_called()
    vehicle_repository.update.assert_not_called()
    vehicle_repository.delete.assert_not_called()


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    vehicle_repository,
):
    vehicle_repository.get_by_id.side_effect = RuntimeError(
        "repository error",
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        use_case.execute(
            vehicle_id="vehicle-1",
        )


# ============================================================
# DIFFERENT VEHICLES
# ============================================================


@pytest.mark.parametrize(
    "vehicle_id",
    [
        "vehicle-1",
        "vehicle-2",
        "abc-123",
        "550e8400-e29b-41d4-a716-446655440000",
    ],
)
def test_execute_supports_different_vehicle_ids(
    vehicle_id,
    use_case,
    vehicle_repository,
):
    vehicle = Mock(
        id=vehicle_id,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(
        vehicle_id=vehicle_id,
    )

    assert result is vehicle

    vehicle_repository.get_by_id.assert_called_once_with(
        vehicle_id,
    )


# ============================================================
# NO WRITES
# ============================================================


def test_execute_does_not_modify_vehicle(
    use_case,
    vehicle_repository,
):
    vehicle = Mock(
        id="vehicle-1",
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(
        vehicle_id="vehicle-1",
    )

    assert result is vehicle

    vehicle_repository.create.assert_not_called()
    vehicle_repository.update.assert_not_called()
    vehicle_repository.delete.assert_not_called()