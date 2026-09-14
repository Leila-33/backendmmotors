from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType

from modules.vehicles.application.dtos.admin.set_availability_dto import (
    SetAvailabilityDTO,
)
from modules.vehicles.application.results.admin.set_availability_result import (
    SetAvailabilityResult,
)
from modules.vehicles.application.use_cases.admin.set_availability import (
    SetAvailabilityUseCase,
)

from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleAvailabilityAlreadySet,
    VehicleNotFound,
)


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    vehicle_id="vehicle-1",
    admin_id="admin-1",
    value=True,
):
    return SetAvailabilityDTO(
        vehicle_id=vehicle_id,
        admin_id=admin_id,
        value=value,
    )


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
    is_available=False,
):
    return Mock(
        id=vehicle_id,
        is_available=is_available,
        status=VehicleStatus.AVAILABLE,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def uow():
    return Mock()


@pytest.fixture
def use_case(
    vehicle_repository,
    event_service,
    uow,
):
    return SetAvailabilityUseCase(
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        unit_of_work=uow,
    )


# ============================================================
# SUCCESS — AVAILABLE
# ============================================================


def test_vehicle_can_become_available(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto(
        value=True,
    )

    vehicle = make_vehicle(
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    assert isinstance(
        result,
        SetAvailabilityResult,
    )

    assert result.vehicle_id == "vehicle-1"

    assert result.status == (
        VehicleStatus.AVAILABLE.value
    )

    assert result.is_available is True

    assert result.message == "Véhicule disponible"

    assert vehicle.is_available is True

    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    event_service.log.assert_called_once()

    uow.commit.assert_called_once()

    uow.rollback.assert_not_called()


# ============================================================
# SUCCESS — UNAVAILABLE
# ============================================================


def test_vehicle_can_become_unavailable(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto(
        value=False,
    )

    vehicle = make_vehicle(
        is_available=True,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    assert isinstance(
        result,
        SetAvailabilityResult,
    )

    assert result.vehicle_id == "vehicle-1"

    assert result.status == (
        VehicleStatus.AVAILABLE.value
    )

    assert result.is_available is False

    assert result.message == "Véhicule indisponible"

    assert vehicle.is_available is False

    vehicle_repository.update.assert_called_once_with(
        vehicle
    )

    event_service.log.assert_called_once()

    uow.commit.assert_called_once()

    uow.rollback.assert_not_called()


# ============================================================
# VEHICLE NOT FOUND
# ============================================================


def test_vehicle_not_found(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-1"
    )

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()

    # Important:
    # VehicleNotFound happens BEFORE the try block.
    uow.rollback.assert_not_called()


# ============================================================
# AVAILABILITY ALREADY SET
# ============================================================


@pytest.mark.parametrize(
    "current_value, requested_value",
    [
        (False, False),
        (True, True),
    ],
)
def test_same_availability_value_is_rejected(
    current_value,
    requested_value,
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto(
        value=requested_value,
    )

    vehicle = make_vehicle(
        is_available=current_value,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    with pytest.raises(VehicleAvailabilityAlreadySet):
        use_case.execute(dto)

    assert vehicle.is_available == current_value

    vehicle_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    uow.commit.assert_not_called()

    # This validation also happens BEFORE the try block.
    uow.rollback.assert_not_called()


# ============================================================
# OLD / NEW VALUE
# ============================================================


def test_old_and_new_values_are_kept_for_event(
    use_case,
    vehicle_repository,
    event_service,
):
    dto = make_dto(
        value=True,
    )

    vehicle = make_vehicle(
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    call_kwargs = event_service.log.call_args.kwargs

    assert call_kwargs["event_metadata"] == {
        "old_value": False,
        "new_value": True,
    }


def test_old_value_is_false_when_vehicle_becomes_available(
    use_case,
    vehicle_repository,
    event_service,
):
    dto = make_dto(
        value=True,
    )

    vehicle = make_vehicle(
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    metadata = (
        event_service.log.call_args.kwargs[
            "event_metadata"
        ]
    )

    assert metadata["old_value"] is False
    assert metadata["new_value"] is True


def test_old_value_is_true_when_vehicle_becomes_unavailable(
    use_case,
    vehicle_repository,
    event_service,
):
    dto = make_dto(
        value=False,
    )

    vehicle = make_vehicle(
        is_available=True,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    metadata = (
        event_service.log.call_args.kwargs[
            "event_metadata"
        ]
    )

    assert metadata["old_value"] is True
    assert metadata["new_value"] is False


# ============================================================
# EVENT
# ============================================================


def test_availability_changed_event_is_logged(
    use_case,
    vehicle_repository,
    event_service,
):
    dto = make_dto(
        vehicle_id="vehicle-42",
        admin_id="admin-99",
        value=True,
    )

    vehicle = make_vehicle(
        vehicle_id="vehicle-42",
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    event_service.log.assert_called_once()

    call_kwargs = event_service.log.call_args.kwargs

    assert call_kwargs["type"] == (
        EventType.VEHICLE_AVAILABILITY_CHANGED
    )

    assert call_kwargs["message"] == (
        "Disponibilité du véhicule modifiée"
    )

    assert call_kwargs["vehicle_id"] == (
        "vehicle-42"
    )

    assert call_kwargs["user_id"] == (
        "admin-99"
    )

    assert call_kwargs["event_metadata"] == {
        "old_value": False,
        "new_value": True,
    }


# ============================================================
# COMMIT
# ============================================================


def test_commit_is_called_on_success(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto(
        value=True,
    )

    vehicle = make_vehicle(
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    use_case.execute(dto)

    uow.commit.assert_called_once()

    uow.rollback.assert_not_called()


def test_update_happens_before_event_and_commit(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto(
        value=True,
    )

    vehicle = make_vehicle(
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    call_order = []

    vehicle_repository.update.side_effect = (
        lambda vehicle: call_order.append("update")
    )

    event_service.log.side_effect = (
        lambda **kwargs: call_order.append("event")
    )

    uow.commit.side_effect = (
        lambda: call_order.append("commit")
    )

    use_case.execute(dto)

    assert call_order == [
        "update",
        "event",
        "commit",
    ]


# ============================================================
# RESULT
# ============================================================


@pytest.mark.parametrize(
    "old_value, new_value, expected_message",
    [
        (
            False,
            True,
            "Véhicule disponible",
        ),
        (
            True,
            False,
            "Véhicule indisponible",
        ),
    ],
)
def test_result_contains_expected_values(
    old_value,
    new_value,
    expected_message,
    use_case,
    vehicle_repository,
):
    dto = make_dto(
        value=new_value,
    )

    vehicle = make_vehicle(
        vehicle_id="vehicle-99",
        is_available=old_value,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    assert isinstance(
        result,
        SetAvailabilityResult,
    )

    assert result.vehicle_id == "vehicle-99"

    assert result.status == (
        VehicleStatus.AVAILABLE.value
    )

    assert result.is_available is new_value

    assert result.message == expected_message


# ============================================================
# REPOSITORY UPDATE ERROR
# ============================================================


def test_update_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto(
        value=True,
    )

    vehicle = make_vehicle(
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    vehicle_repository.update.side_effect = RuntimeError(
        "update error"
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        use_case.execute(dto)

    uow.commit.assert_not_called()

    uow.rollback.assert_called_once()


# ============================================================
# EVENT ERROR
# ============================================================


def test_event_error_rolls_back(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto(
        value=True,
    )

    vehicle = make_vehicle(
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(dto)

    uow.commit.assert_not_called()

    uow.rollback.assert_called_once()


# ============================================================
# COMMIT ERROR
# ============================================================


def test_commit_error_rolls_back(
    use_case,
    vehicle_repository,
    uow,
):
    dto = make_dto(
        value=True,
    )

    vehicle = make_vehicle(
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    uow.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(dto)

    uow.commit.assert_called_once()

    uow.rollback.assert_called_once()


# ============================================================
# DIFFERENT VEHICLE IDS
# ============================================================


@pytest.mark.parametrize(
    "vehicle_id",
    [
        "vehicle-1",
        "vehicle-42",
        "vehicle-99",
        "550e8400-e29b-41d4-a716-446655440000",
    ],
)
def test_execute_uses_exact_vehicle_id(
    vehicle_id,
    use_case,
    vehicle_repository,
):
    dto = make_dto(
        vehicle_id=vehicle_id,
        value=True,
    )

    vehicle = make_vehicle(
        vehicle_id=vehicle_id,
        is_available=False,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        vehicle_id
    )

    assert result.vehicle_id == vehicle_id


# ============================================================
# NO UNEXPECTED CALLS ON VALIDATION FAILURE
# ============================================================


def test_no_write_operations_when_vehicle_not_found(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(dto)

    vehicle_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    uow.commit.assert_not_called()


def test_no_write_operations_when_availability_is_already_set(
    use_case,
    vehicle_repository,
    event_service,
    uow,
):
    dto = make_dto(
        value=True,
    )

    vehicle = make_vehicle(
        is_available=True,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    with pytest.raises(VehicleAvailabilityAlreadySet):
        use_case.execute(dto)

    vehicle_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    uow.commit.assert_not_called()