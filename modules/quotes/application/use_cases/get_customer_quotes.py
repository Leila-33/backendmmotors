from modules.quotes.infrastructure.mappers.quote_mapper import QuoteMapper
class GetCustomerQuotesUseCase:


    def __init__(
        self,
        quote_repository,
    ):
        self.quote_repository = (
            quote_repository
        )


    def execute(
        self,
        customer_id: str,
    ):

        quotes = (
            self.quote_repository
            .find_by_customer(
                customer_id
            )
        )

        return [
            QuoteMapper.to_list_response(
                quote
            )
            for quote in quotes
        ]