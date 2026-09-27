from datetime import date

import pytest

from modules.applications.application.services.rental_duration_calculator import (
    RentalDurationCalculator,
)
from modules.reservations.domain.exceptions import (
    InvalidReservationDates,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def calculator():
    return RentalDurationCalculator()


# ============================================================
# VALID DATES
# ============================================================


def test_calculate_one_day(
    calculator,
):
    start_date = date(2026, 9, 27)
    end_date = date(2026, 9, 27)

    result = calculator.calculate(
        start_date=start_date,
        end_date=end_date,
    )

    assert result == 1


def test_calculate_two_days(
    calculator,
):
    start_date = date(2026, 9, 27)
    end_date = date(2026, 9, 28)

    result = calculator.calculate(
        start_date=start_date,
        end_date=end_date,
    )

    assert result == 2


def test_calculate_multiple_days(
    calculator,
):
    start_date = date(2026, 9, 27)
    end_date = date(2026, 10, 1)

    result = calculator.calculate(
        start_date=start_date,
        end_date=end_date,
    )

    assert result == 5


# ============================================================
# INVALID DATES
# ============================================================


def test_end_date_before_start_date_raises_exception(
    calculator,
):
    start_date = date(2026, 9, 28)
    end_date = date(2026, 9, 27)

    with pytest.raises(InvalidReservationDates):
        calculator.calculate(
            start_date=start_date,
            end_date=end_date,
        )


# ============================================================
# BOUNDARY CASE
# ============================================================


def test_same_date_is_counted_as_one_rental_day(
    calculator,
):
    start_date = date(2026, 12, 31)
    end_date = date(2026, 12, 31)

    result = calculator.calculate(
        start_date=start_date,
        end_date=end_date,
    )

    assert result == 1