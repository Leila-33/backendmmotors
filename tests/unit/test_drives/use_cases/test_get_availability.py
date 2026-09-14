from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from modules.test_drives.application.dtos.get_availability_dto import (
    GetAvailabilityDTO,
)
from modules.test_drives.application.results.get_availability_result import (
    GetAvailabilityResult,
)
from modules.test_drives.application.use_cases.get_availability import (
    GetAvailabilityUseCase,
)
from modules.test_drives.domain.exceptions import (
    InvalidAvailabilityDate,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.vehicles.domain.exceptions import (
    VehicleNotAvailableForTestDrive,
    VehicleNotFound,
)


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    vehicle_id: str = "vehicle-1",
    selected_date: date | None = None,
):
    if selected_date is None:
        selected_date = date.today() + timedelta(
            days=1
        )

    return GetAvailabilityDTO(
        vehicle_id=vehicle_id,
        date=selected_date,
    )


def make_vehicle(
    *,
    vehicle_id: str = "vehicle-1",
    status: VehicleStatus = VehicleStatus.PUBLISHED,
):
    vehicle = Mock()

    vehicle.id = vehicle_id
    vehicle.status = status

    return vehicle


def make_availability_data(
    *,
    selected_date: date | None = None,
):
    if selected_date is None:
        selected_date = date.today() + timedelta(
            days=1
        )

    return {
        "date": selected_date,
        "timezone": "Europe/Paris",
        "available_slots": [
            "09:00",
            "10:00",
            "11:00",
            "14:00",
            "15:00",
        ],
    }


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def use_case(
    repository,
    vehicle_repository,
):
    return GetAvailabilityUseCase(
        repository=repository,
        vehicle_repository=vehicle_repository,
    )


@pytest.fixture
def dto():
    return make_dto()


@pytest.fixture
def vehicle():
    return make_vehicle()


# ============================================================
# VEHICLE NOT FOUND
# ============================================================


def test_vehicle_not_found(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(
        VehicleNotFound
    ):
        use_case.execute(
            dto=dto
        )

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    repository.get_day_availability.assert_not_called()


# ============================================================
# VEHICLE AVAILABILITY
# ============================================================


@pytest.mark.parametrize(
    "status",
    [
        status
        for status in VehicleStatus
        if status != VehicleStatus.PUBLISHED
    ],
)
def test_vehicle_not_published_cannot_be_used_for_test_drive(
    status,
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle(
        status=status
    )

    with pytest.raises(
        VehicleNotAvailableForTestDrive
    ):
        use_case.execute(
            dto=dto
        )

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    repository.get_day_availability.assert_not_called()


def test_published_vehicle_can_be_checked(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    data = make_availability_data(
        selected_date=dto.date
    )

    repository.get_day_availability.return_value = data

    result = use_case.execute(
        dto=dto
    )

    assert isinstance(
        result,
        GetAvailabilityResult,
    )


# ============================================================
# DATE
# ============================================================


def test_past_date_is_rejected(
    use_case,
    vehicle_repository,
    repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    dto = make_dto(
        selected_date=date.today() - timedelta(
            days=1
        )
    )

    with pytest.raises(
        InvalidAvailabilityDate
    ):
        use_case.execute(
            dto=dto
        )

    repository.get_day_availability.assert_not_called()


def test_today_is_accepted(
    use_case,
    vehicle_repository,
    repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    dto = make_dto(
        selected_date=date.today()
    )

    data = make_availability_data(
        selected_date=dto.date
    )

    repository.get_day_availability.return_value = data

    result = use_case.execute(
        dto=dto
    )

    assert isinstance(
        result,
        GetAvailabilityResult,
    )

    repository.get_day_availability.assert_called_once_with(
        vehicle_id=dto.vehicle_id,
        selected_date=dto.date,
    )


def test_future_date_is_accepted(
    use_case,
    vehicle_repository,
    repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    future_date = date.today() + timedelta(
        days=30
    )

    dto = make_dto(
        selected_date=future_date
    )

    data = make_availability_data(
        selected_date=future_date
    )

    repository.get_day_availability.return_value = data

    result = use_case.execute(
        dto=dto
    )

    assert isinstance(
        result,
        GetAvailabilityResult,
    )


# ============================================================
# REPOSITORY
# ============================================================


def test_repository_is_called_with_vehicle_and_date(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    data = make_availability_data(
        selected_date=dto.date
    )

    repository.get_day_availability.return_value = data

    use_case.execute(
        dto=dto
    )

    repository.get_day_availability.assert_called_once_with(
        vehicle_id=dto.vehicle_id,
        selected_date=dto.date,
    )


def test_repository_result_is_used(
    use_case,
    vehicle_repository,
    repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    dto = make_dto()

    data = {
        "date": dto.date,
        "timezone": "Europe/Paris",
        "available_slots": [
            "08:30",
            "12:00",
            "16:30",
        ],
    }

    repository.get_day_availability.return_value = data

    result = use_case.execute(
        dto=dto
    )

    assert result.date == dto.date

    assert result.timezone == "Europe/Paris"

    assert result.available_slots == [
        "08:30",
        "12:00",
        "16:30",
    ]


# ============================================================
# RESULT
# ============================================================


def test_result_type(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    repository.get_day_availability.return_value = (
        make_availability_data(
            selected_date=dto.date
        )
    )

    result = use_case.execute(
        dto=dto
    )

    assert isinstance(
        result,
        GetAvailabilityResult,
    )


def test_result_contains_date(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    repository.get_day_availability.return_value = {
        "date": dto.date,
        "timezone": "Europe/Paris",
        "available_slots": [],
    }

    result = use_case.execute(
        dto=dto
    )

    assert result.date == dto.date


def test_result_contains_timezone(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    repository.get_day_availability.return_value = {
        "date": dto.date,
        "timezone": "Europe/Paris",
        "available_slots": [],
    }

    result = use_case.execute(
        dto=dto
    )

    assert result.timezone == "Europe/Paris"


def test_result_contains_available_slots(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    slots = [
        "09:00",
        "10:00",
        "14:00",
    ]

    repository.get_day_availability.return_value = {
        "date": dto.date,
        "timezone": "Europe/Paris",
        "available_slots": slots,
    }

    result = use_case.execute(
        dto=dto
    )

    assert result.available_slots == slots


@pytest.mark.parametrize(
    "slots",
    [
        [],
        ["09:00"],
        ["09:00", "10:00"],
        ["09:00", "10:00", "11:00", "14:00", "15:00"],
    ],
)
def test_available_slots_are_preserved(
    slots,
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    repository.get_day_availability.return_value = {
        "date": dto.date,
        "timezone": "Europe/Paris",
        "available_slots": slots,
    }

    result = use_case.execute(
        dto=dto
    )

    assert result.available_slots == slots


# ============================================================
# DIFFERENT TIMEZONES
# ============================================================


@pytest.mark.parametrize(
    "timezone_name",
    [
        "Europe/Paris",
        "UTC",
        "Europe/London",
        "America/New_York",
    ],
)
def test_timezone_is_preserved(
    timezone_name,
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    repository.get_day_availability.return_value = {
        "date": dto.date,
        "timezone": timezone_name,
        "available_slots": [],
    }

    result = use_case.execute(
        dto=dto
    )

    assert result.timezone == timezone_name


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    repository.get_day_availability.side_effect = (
        RuntimeError(
            "availability repository error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="availability repository error",
    ):
        use_case.execute(
            dto=dto
        )


def test_vehicle_repository_error_is_propagated(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.side_effect = (
        RuntimeError(
            "vehicle repository error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="vehicle repository error",
    ):
        use_case.execute(
            dto=dto
        )

    repository.get_day_availability.assert_not_called()


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_vehicle_not_found_does_not_query_availability(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(
        VehicleNotFound
    ):
        use_case.execute(
            dto=dto
        )

    repository.get_day_availability.assert_not_called()


def test_invalid_vehicle_does_not_query_availability(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle(
        status=next(
            status
            for status in VehicleStatus
            if status != VehicleStatus.PUBLISHED
        )
    )

    with pytest.raises(
        VehicleNotAvailableForTestDrive
    ):
        use_case.execute(
            dto=dto
        )

    repository.get_day_availability.assert_not_called()


def test_past_date_does_not_query_availability(
    use_case,
    vehicle_repository,
    repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    dto = make_dto(
        selected_date=date.today() - timedelta(
            days=1
        )
    )

    with pytest.raises(
        InvalidAvailabilityDate
    ):
        use_case.execute(
            dto=dto
        )

    repository.get_day_availability.assert_not_called()


def test_success_only_reads_data(
    use_case,
    vehicle_repository,
    repository,
    dto,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    repository.get_day_availability.return_value = (
        make_availability_data(
            selected_date=dto.date
        )
    )

    use_case.execute(
        dto=dto
    )

    vehicle_repository.get_by_id.assert_called_once_with(
        dto.vehicle_id
    )

    repository.get_day_availability.assert_called_once_with(
        vehicle_id=dto.vehicle_id,
        selected_date=dto.date,
    )

    # Repository de disponibilité : aucune opération
    # de modification attendue.
    repository.create.assert_not_called()
    repository.update.assert_not_called()
    repository.delete.assert_not_called()