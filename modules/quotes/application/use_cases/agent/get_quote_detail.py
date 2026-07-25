from modules.quotes.domain.exceptions import QuoteNotFound
from modules.quotes.infrastructure.mappers.quote_mapper import QuoteMapper

class GetQuoteDetailUseCase:

    def __init__(
        self,
        quote_repository,
        authorization,
    ):
        self.quote_repository = quote_repository
        self.authorization = authorization

    def execute(
        self,
        quote_id: str,
        agent_id: str,
    ):

        quote = self.quote_repository.find_by_id(
            quote_id
        )

        if not quote:
            raise QuoteNotFound()

        self.authorization.check_owner(
            quote.lead,
            agent_id,
        )

        return QuoteMapper.to_detail_response(
            quote
        )