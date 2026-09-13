from unittest.mock import Mock

import pytest

from modules.quotes.application.use_cases.get_customer_quotes import (
    GetCustomerQuotesUseCase,
)
from modules.quotes.application.dtos.customer_id_dto import (
    CustomerIdDto,
)


@pytest.fixture
def quote_repository():
    return Mock()


@pytest.fixture
def use_case(quote_repository):
    return GetCustomerQuotesUseCase(
        quote_repository=quote_repository,
    )


@pytest.fixture
def dto():
    return CustomerIdDto(
        customer_id="customer-123",
    )


def test_execute_returns_customer_quotes(
    use_case,
    quote_repository,
    dto,
):
    quotes = [
        Mock(id="quote-1"),
        Mock(id="quote-2"),
    ]

    quote_repository.find_by_customer.return_value = quotes

    result = use_case.execute(dto)

    quote_repository.find_by_customer.assert_called_once_with(
        "customer-123",
    )

    assert result.quotes is quotes
    assert len(result.quotes) == 2


def test_execute_returns_empty_list_when_customer_has_no_quotes(
    use_case,
    quote_repository,
    dto,
):
    quote_repository.find_by_customer.return_value = []

    result = use_case.execute(dto)

    quote_repository.find_by_customer.assert_called_once_with(
        "customer-123",
    )

    assert result.quotes == []


def test_execute_propagates_repository_error(
    use_case,
    quote_repository,
    dto,
):
    quote_repository.find_by_customer.side_effect = (
        RuntimeError("Database error")
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    quote_repository.find_by_customer.assert_called_once_with(
        "customer-123",
    )