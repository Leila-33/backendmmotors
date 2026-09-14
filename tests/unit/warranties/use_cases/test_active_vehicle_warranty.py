from datetime import datetime
from unittest.mock import Mock

import pytest
from dateutil.relativedelta import relativedelta

from modules.applications.domain.enums import EventType

from modules.warranties.application.dtos.activate_vehicle_warranty_dto import (
    ActivateVehicleWarrantyDTO,
)
from modules.warranties.application.use_cases.activate_vehicle_warranty import (
    ActivateVehicleWarrantyUseCase,
)

from modules.vehicles.domain.exceptions import VehicleNotFound

from modules.warranties.domain.exceptions import (
    VehicleWarrantyNotAssigned,
    WarrantyPlanNotFound,
)


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    vehicle_id="vehicle-1",
    user_id="user-1",
    mileage=None,
):
    return ActivateVehicleWarrantyDTO(
        vehicle_id=vehicle_id,
        user_id=user_id,
        mileage=mileage,
    )


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
    mileage=50000,
    warranty=None,
):
    return Mock(
        id=vehicle_id,
        mileage=mileage,
        warranty=warranty,
    )


def make_warranty(
    *,
    warranty_id="warranty-1",
    warranty_plan_id="plan-1",
    is_active=False,
):
    warranty = Mock(
        id=warranty_id,
        warranty_plan_id=warranty_plan_id,
        is_active=is_active,
    )

    return warranty


def make_plan(
    *,
    plan_id="plan-1",
    duration_months=12,
    mileage_limit=100000,
):
    return Mock(
        id=plan_id,
        duration_months=duration_months,
        mileage_limit=mileage_limit,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def warranty_repository():
    return Mock()


@pytest.fixture
def warranty_plan_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def use_case(
    vehicle_repository,
    warranty_repository,
    warranty_plan_repository,
    event_service,
):
    return ActivateVehicleWarrantyUseCase(
        vehicle_repository=vehicle_repository,
        warranty_repository=warranty_repository,
        warranty_plan_repository=warranty_plan_repository,
        event_service=event_service,
    )


# ============================================================
# SUCCESS
# ============================================================


def test_activate_vehicle_warranty_success(
    use_case,
    vehicle_repository,
    warranty_repository,
    warranty_plan_repository,
    event_service,
):
    dto = make_dto(
        vehicle_id="vehicle-1",
        user_id="user-1",
        mileage=55000,
    )

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
        mileage=50000,
    )

    plan = make_plan(
        duration_months=12,
        mileage_limit=100000,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    result = use_case.execute(dto)

    assert result is warranty

    warranty.activate.assert_called_once()

    warranty_repository.update.assert_called_once_with(
        warranty
    )

    event_service.log.assert_called_once()


# ============================================================
# VEHICLE NOT FOUND
# ============================================================


def test_vehicle_not_found(
    use_case,
    vehicle_repository,
    warranty_repository,
    warranty_plan_repository,
    event_service,
):
    dto = make_dto()

    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-1"
    )

    warranty_plan_repository.get_by_id.assert_not_called()

    warranty_repository.update.assert_not_called()

    event_service.log.assert_not_called()


# ============================================================
# WARRANTY NOT ASSIGNED
# ============================================================


def test_vehicle_warranty_not_assigned(
    use_case,
    vehicle_repository,
    warranty_repository,
    warranty_plan_repository,
    event_service,
):
    dto = make_dto()

    vehicle = make_vehicle(
        warranty=None,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    with pytest.raises(VehicleWarrantyNotAssigned):
        use_case.execute(dto)

    warranty_plan_repository.get_by_id.assert_not_called()

    warranty_repository.update.assert_not_called()

    event_service.log.assert_not_called()


# ============================================================
# IDEMPOTENCY
# ============================================================


def test_already_active_warranty_is_returned(
    use_case,
    vehicle_repository,
    warranty_repository,
    warranty_plan_repository,
    event_service,
):
    dto = make_dto()

    warranty = make_warranty(
        is_active=True,
    )

    vehicle = make_vehicle(
        warranty=warranty,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    assert result is warranty

    warranty.activate.assert_not_called()

    warranty_plan_repository.get_by_id.assert_not_called()

    warranty_repository.update.assert_not_called()

    event_service.log.assert_not_called()


def test_already_active_warranty_does_not_change(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    warranty = make_warranty(
        is_active=True,
    )

    vehicle = make_vehicle(
        warranty=warranty,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    assert result is warranty
    assert warranty.is_active is True


# ============================================================
# WARRANTY PLAN
# ============================================================


def test_warranty_plan_is_loaded(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
):
    dto = make_dto()

    warranty = make_warranty(
        warranty_plan_id="plan-42",
    )

    vehicle = make_vehicle(
        warranty=warranty,
    )

    plan = make_plan(
        plan_id="plan-42",
    )

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    warranty_plan_repository.get_by_id.assert_called_once_with(
        "plan-42"
    )


def test_warranty_plan_not_found(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
    warranty_repository,
    event_service,
):
    dto = make_dto()

    warranty = make_warranty(
        warranty_plan_id="plan-1",
    )

    vehicle = make_vehicle(
        warranty=warranty,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = None

    with pytest.raises(WarrantyPlanNotFound):
        use_case.execute(dto)

    warranty.activate.assert_not_called()

    warranty_repository.update.assert_not_called()

    event_service.log.assert_not_called()


# ============================================================
# MILEAGE
# ============================================================


def test_dto_mileage_is_used_when_provided(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
):
    dto = make_dto(
        mileage=75000,
    )

    warranty = make_warranty()

    vehicle = make_vehicle(
        mileage=50000,
        warranty=warranty,
    )

    plan = make_plan()

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    kwargs = warranty.activate.call_args.kwargs

    assert kwargs["current_mileage"] == 75000


def test_vehicle_mileage_is_used_when_dto_mileage_is_none(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
):
    dto = make_dto(
        mileage=None,
    )

    warranty = make_warranty()

    vehicle = make_vehicle(
        mileage=62000,
        warranty=warranty,
    )

    plan = make_plan()

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    kwargs = warranty.activate.call_args.kwargs

    assert kwargs["current_mileage"] == 62000


# ============================================================
# ACTIVATION PARAMETERS
# ============================================================


def test_warranty_is_activated_with_plan_mileage_limit(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
):
    dto = make_dto(
        mileage=60000,
    )

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
    )

    plan = make_plan(
        mileage_limit=120000,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    kwargs = warranty.activate.call_args.kwargs

    assert kwargs["current_mileage"] == 60000

    assert kwargs["max_mileage"] == 120000


def test_activation_start_date_is_timezone_aware(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
):
    dto = make_dto()

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
    )

    plan = make_plan(
        duration_months=12,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    kwargs = warranty.activate.call_args.kwargs

    start_date = kwargs["start_date"]

    assert isinstance(
        start_date,
        datetime,
    )

    assert start_date.tzinfo is not None

    assert start_date.utcoffset() is not None


def test_end_date_matches_plan_duration(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
):
    dto = make_dto()

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
    )

    plan = make_plan(
        duration_months=18,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    kwargs = warranty.activate.call_args.kwargs

    start_date = kwargs["start_date"]
    end_date = kwargs["end_date"]

    expected_end_date = (
        start_date
        + relativedelta(months=18)
    )

    assert end_date == expected_end_date


@pytest.mark.parametrize(
    "duration_months",
    [
        1,
        3,
        6,
        12,
        24,
    ],
)
def test_end_date_uses_exact_plan_duration(
    duration_months,
    use_case,
    vehicle_repository,
    warranty_plan_repository,
):
    dto = make_dto()

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
    )

    plan = make_plan(
        duration_months=duration_months,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    kwargs = warranty.activate.call_args.kwargs

    assert kwargs["end_date"] == (
        kwargs["start_date"]
        + relativedelta(
            months=duration_months
        )
    )


# ============================================================
# PERSISTENCE
# ============================================================


def test_warranty_is_updated(
    use_case,
    vehicle_repository,
    warranty_repository,
    warranty_plan_repository,
):
    dto = make_dto()

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
    )

    plan = make_plan()

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    warranty_repository.update.assert_called_once_with(
        warranty
    )


# ============================================================
# EVENT
# ============================================================


def test_warranty_activated_event_is_logged(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
    event_service,
):
    dto = make_dto(
        vehicle_id="vehicle-42",
        user_id="user-99",
        mileage=65000,
    )

    warranty = make_warranty(
        warranty_id="warranty-42",
        warranty_plan_id="plan-42",
    )

    vehicle = make_vehicle(
        vehicle_id="vehicle-42",
        warranty=warranty,
        mileage=50000,
    )

    plan = make_plan(
        plan_id="plan-42",
        duration_months=24,
        mileage_limit=150000,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    event_service.log.assert_called_once()

    kwargs = event_service.log.call_args.kwargs

    assert kwargs["vehicle_id"] == "vehicle-42"

    assert kwargs["user_id"] == "user-99"

    assert kwargs["type"] == (
        EventType.WARRANTY_ACTIVATED
    )

    assert kwargs["message"] == (
        "Garantie activée."
    )

    assert kwargs["event_metadata"] == {
        "warranty_id": "warranty-42",
        "warranty_plan_id": "plan-42",
        "duration_months": 24,
        "max_mileage": 150000,
        "current_mileage": 65000,
    }


def test_event_uses_vehicle_mileage_when_dto_mileage_is_none(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
    event_service,
):
    dto = make_dto(
        mileage=None,
    )

    warranty = make_warranty()

    vehicle = make_vehicle(
        mileage=73000,
        warranty=warranty,
    )

    plan = make_plan()

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    use_case.execute(dto)

    metadata = (
        event_service.log.call_args.kwargs[
            "event_metadata"
        ]
    )

    assert metadata["current_mileage"] == 73000


# ============================================================
# RETURN VALUE
# ============================================================


def test_use_case_returns_same_warranty(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
):
    dto = make_dto()

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
    )

    plan = make_plan()

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    result = use_case.execute(dto)

    assert result is warranty


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_vehicle_repository_error_is_propagated(
    use_case,
    vehicle_repository,
):
    dto = make_dto()

    vehicle_repository.get_by_id.side_effect = RuntimeError(
        "vehicle repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="vehicle repository error",
    ):
        use_case.execute(dto)


def test_warranty_plan_repository_error_is_propagated(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
):
    dto = make_dto()

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.side_effect = (
        RuntimeError(
            "warranty plan repository error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="warranty plan repository error",
    ):
        use_case.execute(dto)


def test_warranty_update_error_is_propagated(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
    warranty_repository,
):
    dto = make_dto()

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
    )

    plan = make_plan()

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    warranty_repository.update.side_effect = (
        RuntimeError(
            "warranty update error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="warranty update error",
    ):
        use_case.execute(dto)


def test_event_error_is_propagated(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
    event_service,
):
    dto = make_dto()

    warranty = make_warranty()

    vehicle = make_vehicle(
        warranty=warranty,
    )

    plan = make_plan()

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(dto)


# ============================================================
# NO UNEXPECTED CALLS ON VALIDATION FAILURE
# ============================================================


def test_no_plan_lookup_when_warranty_is_missing(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
    warranty_repository,
    event_service,
):
    dto = make_dto()

    vehicle = make_vehicle(
        warranty=None,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    with pytest.raises(VehicleWarrantyNotAssigned):
        use_case.execute(dto)

    warranty_plan_repository.get_by_id.assert_not_called()

    warranty_repository.update.assert_not_called()

    event_service.log.assert_not_called()


def test_no_update_or_event_when_warranty_is_already_active(
    use_case,
    vehicle_repository,
    warranty_plan_repository,
    warranty_repository,
    event_service,
):
    dto = make_dto()

    warranty = make_warranty(
        is_active=True,
    )

    vehicle = make_vehicle(
        warranty=warranty,
    )

    vehicle_repository.get_by_id.return_value = vehicle

    result = use_case.execute(dto)

    assert result is warranty

    warranty_plan_repository.get_by_id.assert_not_called()

    warranty_repository.update.assert_not_called()

    event_service.log.assert_not_called()


# ============================================================
# EXACT VEHICLE ID
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
    warranty_plan_repository,
):
    dto = make_dto(
        vehicle_id=vehicle_id,
    )

    warranty = make_warranty()

    vehicle = make_vehicle(
        vehicle_id=vehicle_id,
        warranty=warranty,
    )

    plan = make_plan()

    vehicle_repository.get_by_id.return_value = vehicle

    warranty_plan_repository.get_by_id.return_value = plan

    result = use_case.execute(dto)

    vehicle_repository.get_by_id.assert_called_once_with(
        vehicle_id
    )

    assert result is warranty