from unittest.mock import Mock

import pytest

from modules.quotes.application.use_cases.get_client_quote_action_required_count import (
    GetClientQuoteActionRequiredCountUseCase,
)
from modules.quotes.application.dtos.customer_id_dto import (
    CustomerIdDto,
)


@pytest.fixture
def quote_repository():
    return Mock()


@pytest.fixture
def use_case(quote_repository):
    return GetClientQuoteActionRequiredCountUseCase(
        quote_repository=quote_repository,
    )


def test_execute_returns_action_required_count(
    use_case,
    quote_repository,
):
    quote_repository.count_action_required_by_customer.return_value = 3

    dto = CustomerIdDto(
        customer_id="customer-123",
    )

    result = use_case.execute(dto)

    quote_repository.count_action_required_by_customer.assert_called_once_with(
        "customer-123"
    )

    assert result.count == 3


def test_execute_returns_zero_when_no_action_is_required(
    use_case,
    quote_repository,
):
    quote_repository.count_action_required_by_customer.return_value = 0

    dto = CustomerIdDto(
        customer_id="customer-123",
    )

    result = use_case.execute(dto)

    quote_repository.count_action_required_by_customer.assert_called_once_with(
        "customer-123"
    )

    assert result.count == 0


def test_execute_propagates_repository_error(
    use_case,
    quote_repository,
):
    quote_repository.count_action_required_by_customer.side_effect = (
        RuntimeError("Database error")
    )

    dto = CustomerIdDto(
        customer_id="customer-123",
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    quote_repository.count_action_required_by_customer.assert_called_once_with(
        "customer-123"
    )