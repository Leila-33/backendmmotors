from unittest.mock import Mock

import pytest

from modules.financing.application.dtos.trade_in_estimate_dto import (
    TradeInEstimateDTO,
)
from modules.financing.application.results.trade_in_estimate_result import (
    TradeInEstimateResult,
)
from modules.financing.application.use_cases.estimate_trade_in import (
    EstimateTradeInUseCase,
)
from modules.financing.domain.inputs.trade_in_input import (
    TradeInInput,
)


@pytest.fixture
def trade_in_estimation_service():
    return Mock()


@pytest.fixture
def use_case(trade_in_estimation_service):
    return EstimateTradeInUseCase(
        trade_in_estimation_service=trade_in_estimation_service,
    )


@pytest.fixture
def dto():
    return TradeInEstimateDTO(
        brand="Peugeot",
        model="308",
        year=2022,
        mileage=45000,
        condition="GOOD",
    )


def test_execute_returns_estimation_result(
    use_case,
    trade_in_estimation_service,
    dto,
):
    expected_result = TradeInEstimateResult(
        estimated_value=15000.0,
    )

    trade_in_estimation_service.estimate.return_value = (
        expected_result
    )

    result = use_case.execute(dto)

    trade_in_estimation_service.estimate.assert_called_once()

    trade_input = (
        trade_in_estimation_service
        .estimate
        .call_args.args[0]
    )

    assert isinstance(trade_input, TradeInInput)
    assert trade_input.brand == dto.brand
    assert trade_input.model == dto.model
    assert trade_input.year == dto.year
    assert trade_input.mileage == dto.mileage
    assert trade_input.condition == dto.condition

    assert result is expected_result


def test_execute_propagates_estimation_error(
    use_case,
    trade_in_estimation_service,
    dto,
):
    trade_in_estimation_service.estimate.side_effect = (
        RuntimeError("Estimation error")
    )

    with pytest.raises(
        RuntimeError,
        match="Estimation error",
    ):
        use_case.execute(dto)

    trade_in_estimation_service.estimate.assert_called_once()