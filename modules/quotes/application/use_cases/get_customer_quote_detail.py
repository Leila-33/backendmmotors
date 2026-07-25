from modules.quotes.domain.exceptions import QuoteNotFound, QuoteNotAvailableForCustomer
from modules.quotes.infrastructure.mappers.quote_mapper import QuoteMapper

class GetCustomerQuoteDetailUseCase:

    def __init__(
        self,
        quote_repository,
        application_repository,
    ):
        self.quote_repository = quote_repository
        self.application_repository = application_repository



    def execute(
        self,
        quote_id: str,
        customer_id: str,
    ):

        quote = (
            self.quote_repository
            .find_customer_quote_by_id(
                quote_id,
                customer_id,
            )
        )

        if quote is None:
            raise QuoteNotFound()

        if not quote.can_be_viewed_by_customer():
            raise QuoteNotAvailableForCustomer()

        application = (
            self.application_repository
            .find_by_quote_id(
                quote.id
            )
        )

        return QuoteMapper.to_customer_detail_response(
            quote,
            application.id if application else None,
        )