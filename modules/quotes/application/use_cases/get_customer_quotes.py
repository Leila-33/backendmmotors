from modules.quotes.application.dtos.customer_id_dto import (
    CustomerIdDto,
)
from modules.quotes.application.results.get_customer_quotes_result import (
    GetCustomerQuotesResult
)


class GetCustomerQuotesUseCase:

    def __init__(
        self,
        quote_repository,
    ):
        self.quote_repository = quote_repository

    def execute(
        self,
        dto: CustomerIdDto,
    ) -> GetCustomerQuotesResult:

        quotes = (
            self.quote_repository
            .find_by_customer(
                dto.customer_id
            )
        )

        return GetCustomerQuotesResult(
            quotes=quotes
        )