from modules.quotes.application.dtos.get_customer_quotes_dto import (
    GetCustomerQuotesDTO
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
        dto: GetCustomerQuotesDTO,
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