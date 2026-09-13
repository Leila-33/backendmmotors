from unittest.mock import Mock

import pytest

from modules.quotes.application.use_cases.get_customer_quote_detail import (
    GetCustomerQuoteDetailUseCase,
)
from modules.quotes.application.dtos.customer_quote_dto import (
    CustomerQuoteDTO,
)
from modules.quotes.domain.exceptions import (
    QuoteNotFound,
    QuoteNotAvailableForCustomer,
)


@pytest.fixture
def quote_repository():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def use_case(quote_repository, application_repository):
    return GetCustomerQuoteDetailUseCase(
        quote_repository=quote_repository,
        application_repository=application_repository,
    )


@pytest.fixture
def dto():
    return CustomerQuoteDTO(
        quote_id="quote-123",
        customer_id="customer-123",
    )


def make_quote(can_be_viewed=True):
    quote = Mock()
    quote.id = "quote-123"
    quote.lead_id = "lead-123"
    quote.can_be_viewed_by_customer.return_value = can_be_viewed
    return quote


def test_execute_returns_quote_detail_without_application(
    use_case,
    quote_repository,
    application_repository,
    dto,
):
    quote = make_quote()

    quote_repository.find_customer_quote_by_id.return_value = quote
    application_repository.find_by_quote_id.return_value = None

    result = use_case.execute(dto)

    quote_repository.find_customer_quote_by_id.assert_called_once_with(
        "quote-123",
        "customer-123",
    )

    quote.can_be_viewed_by_customer.assert_called_once_with()

    application_repository.find_by_quote_id.assert_called_once_with(
        "quote-123",
    )

    assert result.quote is quote
    assert result.application_id is None


def test_execute_returns_quote_detail_with_application(
    use_case,
    quote_repository,
    application_repository,
    dto,
):
    quote = make_quote()

    application = Mock()
    application.id = "application-123"

    quote_repository.find_customer_quote_by_id.return_value = quote
    application_repository.find_by_quote_id.return_value = application

    result = use_case.execute(dto)

    quote_repository.find_customer_quote_by_id.assert_called_once_with(
        "quote-123",
        "customer-123",
    )

    quote.can_be_viewed_by_customer.assert_called_once_with()

    application_repository.find_by_quote_id.assert_called_once_with(
        "quote-123",
    )

    assert result.quote is quote
    assert result.application_id == "application-123"


def test_execute_raises_quote_not_found_when_quote_does_not_exist(
    use_case,
    quote_repository,
    application_repository,
    dto,
):
    quote_repository.find_customer_quote_by_id.return_value = None

    with pytest.raises(QuoteNotFound):
        use_case.execute(dto)

    quote_repository.find_customer_quote_by_id.assert_called_once_with(
        "quote-123",
        "customer-123",
    )

    application_repository.find_by_quote_id.assert_not_called()


def test_execute_raises_quote_not_available_when_customer_cannot_view(
    use_case,
    quote_repository,
    application_repository,
    dto,
):
    quote = make_quote(can_be_viewed=False)

    quote_repository.find_customer_quote_by_id.return_value = quote

    with pytest.raises(QuoteNotAvailableForCustomer):
        use_case.execute(dto)

    quote.can_be_viewed_by_customer.assert_called_once_with()

    application_repository.find_by_quote_id.assert_not_called()


def test_execute_propagates_quote_repository_error(
    use_case,
    quote_repository,
    application_repository,
    dto,
):
    quote_repository.find_customer_quote_by_id.side_effect = (
        RuntimeError("Database error")
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    application_repository.find_by_quote_id.assert_not_called()


def test_execute_propagates_application_repository_error(
    use_case,
    quote_repository,
    application_repository,
    dto,
):
    quote = make_quote()

    quote_repository.find_customer_quote_by_id.return_value = quote
    application_repository.find_by_quote_id.side_effect = (
        RuntimeError("Database error")
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    quote.can_be_viewed_by_customer.assert_called_once_with()
    application_repository.find_by_quote_id.assert_called_once_with(
        "quote-123",
    )