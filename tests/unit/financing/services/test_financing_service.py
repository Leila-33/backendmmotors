from unittest.mock import Mock

import pytest

from modules.financing.application.results.financing_result import (
    FinancingResult,
)
from modules.financing.domain.exceptions import (
    InvalidFinancingAmount,
    InvalidFinancingDuration,
)
from modules.financing.domain.inputs.financing_input import (
    FinancingInput,
)
from modules.financing.domain.services.financing_service import (
    FinancingService,
)


@pytest.fixture
def service():
    return FinancingService()


def test_calculate_returns_financing_result(service):
    data = FinancingInput(
        total_price=30000,
        down_payment=5000,
        trade_in_value=3000,
        duration_months=60,
    )

    result = service.calculate(data)

    assert isinstance(result, FinancingResult)
    assert result.financed_amount == 22000
    assert result.monthly_payment == 366.67


def test_calculate_rejects_negative_total_price(service):
    data = FinancingInput(
        total_price=-1,
        down_payment=0,
        trade_in_value=0,
        duration_months=60,
    )

    with pytest.raises(
        InvalidFinancingAmount,
        match="Le prix total ne peut pas être négatif.",
    ):
        service.calculate(data)


def test_calculate_rejects_negative_down_payment(service):
    data = FinancingInput(
        total_price=30000,
        down_payment=-1,
        trade_in_value=0,
        duration_months=60,
    )

    with pytest.raises(
        InvalidFinancingAmount,
        match="L'apport ne peut pas être négatif.",
    ):
        service.calculate(data)


def test_calculate_rejects_negative_trade_in_value(service):
    data = FinancingInput(
        total_price=30000,
        down_payment=0,
        trade_in_value=-1,
        duration_months=60,
    )

    with pytest.raises(
        InvalidFinancingAmount,
        match="La valeur de reprise ne peut pas être négative.",
    ):
        service.calculate(data)


def test_calculate_rejects_down_payment_and_trade_in_exceeding_price(
    service,
):
    data = FinancingInput(
        total_price=30000,
        down_payment=20000,
        trade_in_value=15000,
        duration_months=60,
    )

    with pytest.raises(
        InvalidFinancingAmount,
        match="L'apport et la reprise dépassent le prix du véhicule.",
    ):
        service.calculate(data)


@pytest.mark.parametrize("duration", [12, 18, 30, 72])
def test_calculate_rejects_invalid_duration(
    service,
    duration,
):
    data = FinancingInput(
        total_price=30000,
        down_payment=5000,
        trade_in_value=3000,
        duration_months=duration,
    )

    with pytest.raises(
        InvalidFinancingDuration,
        match="La durée doit être de 24, 36, 48 ou 60 mois.",
    ):
        service.calculate(data)