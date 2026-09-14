from unittest.mock import Mock

import pytest

from modules.vehicles.application.results.admin.get_vehicle_lifecycle_result import (
    GetVehicleLifecycleResult,
)
from modules.vehicles.application.use_cases.admin.get_vehicle_lifecycle import (
    GetVehicleLifecycleUseCase,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def inspection_repository():
    return Mock()


@pytest.fixture
def reconditioning_repository():
    return Mock()


@pytest.fixture
def use_case(
    inspection_repository,
    reconditioning_repository,
):
    return GetVehicleLifecycleUseCase(
        inspection_repository=inspection_repository,
        reconditioning_repository=reconditioning_repository,
    )


# ============================================================
# SUCCESS
# ============================================================


def test_returns_vehicle_lifecycle(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    vehicle_id = "vehicle-1"

    inspection = Mock(
        id="inspection-1",
        vehicle_id=vehicle_id,
    )

    reconditioning = Mock(
        id="reconditioning-1",
        vehicle_id=vehicle_id,
    )

    inspection_repository.get_by_vehicle_id.return_value = (
        inspection
    )

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    result = use_case.execute(vehicle_id)

    assert isinstance(
        result,
        GetVehicleLifecycleResult,
    )

    assert result.inspection is inspection
    assert result.reconditioning is reconditioning


# ============================================================
# REPOSITORY CALLS
# ============================================================


def test_inspection_repository_is_called_with_vehicle_id(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    vehicle_id = "vehicle-42"

    inspection_repository.get_by_vehicle_id.return_value = None
    reconditioning_repository.get_by_vehicle_id.return_value = None

    use_case.execute(vehicle_id)

    inspection_repository.get_by_vehicle_id.assert_called_once_with(
        vehicle_id
    )


def test_reconditioning_repository_is_called_with_vehicle_id(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    vehicle_id = "vehicle-42"

    inspection_repository.get_by_vehicle_id.return_value = None
    reconditioning_repository.get_by_vehicle_id.return_value = None

    use_case.execute(vehicle_id)

    reconditioning_repository.get_by_vehicle_id.assert_called_once_with(
        vehicle_id
    )


def test_both_repositories_are_called_once(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    vehicle_id = "vehicle-1"

    inspection_repository.get_by_vehicle_id.return_value = None
    reconditioning_repository.get_by_vehicle_id.return_value = None

    use_case.execute(vehicle_id)

    inspection_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-1"
    )

    reconditioning_repository.get_by_vehicle_id.assert_called_once_with(
        "vehicle-1"
    )


# ============================================================
# NO INSPECTION
# ============================================================


def test_returns_none_when_inspection_does_not_exist(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    vehicle_id = "vehicle-1"

    inspection_repository.get_by_vehicle_id.return_value = None

    reconditioning = Mock(
        id="reconditioning-1",
        vehicle_id=vehicle_id,
    )

    reconditioning_repository.get_by_vehicle_id.return_value = (
        reconditioning
    )

    result = use_case.execute(vehicle_id)

    assert isinstance(
        result,
        GetVehicleLifecycleResult,
    )

    assert result.inspection is None
    assert result.reconditioning is reconditioning


# ============================================================
# NO RECONDITIONING
# ============================================================


def test_returns_none_when_reconditioning_does_not_exist(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    vehicle_id = "vehicle-1"

    inspection = Mock(
        id="inspection-1",
        vehicle_id=vehicle_id,
    )

    inspection_repository.get_by_vehicle_id.return_value = (
        inspection
    )

    reconditioning_repository.get_by_vehicle_id.return_value = (
        None
    )

    result = use_case.execute(vehicle_id)

    assert isinstance(
        result,
        GetVehicleLifecycleResult,
    )

    assert result.inspection is inspection
    assert result.reconditioning is None


# ============================================================
# NO LIFECYCLE DATA
# ============================================================


def test_returns_empty_lifecycle_when_no_data_exists(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    vehicle_id = "vehicle-1"

    inspection_repository.get_by_vehicle_id.return_value = None
    reconditioning_repository.get_by_vehicle_id.return_value = None

    result = use_case.execute(vehicle_id)

    assert isinstance(
        result,
        GetVehicleLifecycleResult,
    )

    assert result.inspection is None
    assert result.reconditioning is None


# ============================================================
# INSPECTION REPOSITORY ERROR
# ============================================================


def test_inspection_repository_error_is_propagated(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    vehicle_id = "vehicle-1"

    inspection_repository.get_by_vehicle_id.side_effect = (
        RuntimeError(
            "inspection repository error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="inspection repository error",
    ):
        use_case.execute(vehicle_id)

    reconditioning_repository.get_by_vehicle_id.assert_not_called()


# ============================================================
# RECONDITIONING REPOSITORY ERROR
# ============================================================


def test_reconditioning_repository_error_is_propagated(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    vehicle_id = "vehicle-1"

    inspection = Mock(
        id="inspection-1",
        vehicle_id=vehicle_id,
    )

    inspection_repository.get_by_vehicle_id.return_value = (
        inspection
    )

    reconditioning_repository.get_by_vehicle_id.side_effect = (
        RuntimeError(
            "reconditioning repository error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="reconditioning repository error",
    ):
        use_case.execute(vehicle_id)


# ============================================================
# VEHICLE IDS
# ============================================================


@pytest.mark.parametrize(
    "vehicle_id",
    [
        "vehicle-1",
        "vehicle-42",
        "abc-123",
        "550e8400-e29b-41d4-a716-446655440000",
    ],
)
def test_execute_uses_exact_vehicle_id(
    vehicle_id,
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    inspection_repository.get_by_vehicle_id.return_value = None
    reconditioning_repository.get_by_vehicle_id.return_value = None

    use_case.execute(vehicle_id)

    inspection_repository.get_by_vehicle_id.assert_called_once_with(
        vehicle_id
    )

    reconditioning_repository.get_by_vehicle_id.assert_called_once_with(
        vehicle_id
    )


# ============================================================
# NO WRITES
# ============================================================


def test_use_case_does_not_modify_repositories(
    use_case,
    inspection_repository,
    reconditioning_repository,
):
    inspection_repository.get_by_vehicle_id.return_value = None
    reconditioning_repository.get_by_vehicle_id.return_value = None

    use_case.execute("vehicle-1")

    # Le use case est uniquement en lecture.
    # Il ne doit effectuer aucune opération d'écriture.
    for method in [
        "save",
        "create",
        "update",
        "delete",
        "delete_by_vehicle",
    ]:
        if hasattr(inspection_repository, method):
            getattr(
                inspection_repository,
                method,
            ).assert_not_called()

        if hasattr(reconditioning_repository, method):
            getattr(
                reconditioning_repository,
                method,
            ).assert_not_called()