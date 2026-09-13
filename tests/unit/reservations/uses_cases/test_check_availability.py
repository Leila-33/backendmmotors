from unittest.mock import Mock

import pytest

from modules.reservations.application.dtos.check_availability_dto import (
    CheckAvailabilityDTO,
)
from modules.reservations.application.use_cases.check_availability import (
    CheckReservationAvailabilityUseCase,
)


@pytest.fixture
def reservation_repository():
    return Mock()


@pytest.fixture
def use_case(reservation_repository):
    return CheckReservationAvailabilityUseCase(
        reservation_repository=reservation_repository,
    )


@pytest.fixture
def dto():
    return CheckAvailabilityDTO(
        vehicle_id="vehicle-123",
        start_date="2026-09-20",
        end_date="2026-09-25",
    )


def test_execute_returns_true_when_no_overlap(
    use_case,
    reservation_repository,
    dto,
):
    reservation_repository.exists_overlap.return_value = False

    result = use_case.execute(dto)

    assert result is True

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-123",
        start_date=dto.start_date,
        end_date=dto.end_date,
    )


def test_execute_returns_false_when_overlap_exists(
    use_case,
    reservation_repository,
    dto,
):
    reservation_repository.exists_overlap.return_value = True

    result = use_case.execute(dto)

    assert result is False

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-123",
        start_date=dto.start_date,
        end_date=dto.end_date,
    )


def test_execute_propagates_repository_error(
    use_case,
    reservation_repository,
    dto,
):
    reservation_repository.exists_overlap.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-123",
        start_date=dto.start_date,
        end_date=dto.end_date,
    )