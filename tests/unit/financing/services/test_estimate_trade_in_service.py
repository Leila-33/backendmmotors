from unittest.mock import patch

import pytest

from modules.applications.domain.enums import TradeInVehicleCondition
from modules.financing.application.results.trade_in_estimate_result import (
    TradeInEstimateResult,
)
from modules.financing.domain.inputs.trade_in_input import (
    TradeInInput,
)
from modules.financing.domain.services.trade_in_service import (
    TradeInService,
)


@pytest.fixture
def service():
    return TradeInService()


def test_estimate_returns_expected_value(service):
    data = TradeInInput(
        brand="Peugeot",
        model="308",
        year=2024,
        mileage=15000,
        condition=TradeInVehicleCondition.GOOD,
    )

    with patch(
        "modules.financing.domain.services.trade_in_service.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value.year = 2026

        result = service.estimate(data)

    assert isinstance(result, TradeInEstimateResult)

    # Age = 2
    # age_factor = 0.86 ** 2 = 0.7396
    # expected_mileage = 2 * 15000 = 30000
    # mileage_ratio = 15000 / 30000 = 0.5
    # mileage_factor = 1 - 0.5 * 0.1 = 0.95
    # condition_factor = 1.0
    # 20000 * 0.7396 * 0.95 = 14052.4
    assert result.estimated_value == 14052


def test_estimate_handles_future_year_as_zero_age(service):
    data = TradeInInput(
        brand="Peugeot",
        model="308",
        year=2028,
        mileage=15000,
        condition=TradeInVehicleCondition.GOOD,
    )

    with patch(
        "modules.financing.domain.services.trade_in_service.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value.year = 2026

        result = service.estimate(data)

    # Age = max(0, 2026 - 2028) = 0
    # expected_mileage = 15000
    # mileage_ratio = 1
    # mileage_factor = 0.9
    # 20000 * 1 * 0.9 * 1 = 18000
    assert result.estimated_value == 18000


@pytest.mark.parametrize(
    "condition, expected_value",
    [
        (TradeInVehicleCondition.EXCELLENT, 15458),
        (TradeInVehicleCondition.GOOD, 14052),
        (TradeInVehicleCondition.AVERAGE, 11945),
        (TradeInVehicleCondition.POOR, 9837),
    ],
)
def test_estimate_applies_condition_factor(
    service,
    condition,
    expected_value,
):
    data = TradeInInput(
        brand="Peugeot",
        model="308",
        year=2024,
        mileage=15000,
        condition=condition,
    )

    with patch(
        "modules.financing.domain.services.trade_in_service.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value.year = 2026

        result = service.estimate(data)

    assert result.estimated_value == expected_value


def test_estimate_applies_mileage_floor(service):
    data = TradeInInput(
        brand="Peugeot",
        model="308",
        year=2026,
        mileage=1_000_000,
        condition=TradeInVehicleCondition.GOOD,
    )

    with patch(
        "modules.financing.domain.services.trade_in_service.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value.year = 2026

        result = service.estimate(data)

    # Age = 0
    # expected_mileage = 15000
    # mileage_ratio = 1000000 / 15000
    # mileage_factor is capped at 0.4
    # 20000 * 1 * 0.4 = 8000
    assert result.estimated_value == 8000


def test_estimate_applies_minimum_estimated_value(service):
    data = TradeInInput(
        brand="Peugeot",
        model="308",
        year=1950,
        mileage=10_000_000,
        condition=TradeInVehicleCondition.POOR,
    )

    with patch(
        "modules.financing.domain.services.trade_in_service.datetime"
    ) as mock_datetime:
        mock_datetime.now.return_value.year = 2026

        result = service.estimate(data)

    assert result.estimated_value == 1000