import logging

from modules.quotes.domain.exceptions import (
    QuoteNotFound,
)

from modules.quotes.application.dtos.agent.get_quote_detail_dto import (
    GetQuoteDetailDTO,
)

from modules.quotes.application.results.agent.get_quote_detail_result import (
    GetQuoteDetailResult,
)


logger = logging.getLogger(__name__)


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
        dto: GetQuoteDetailDTO,
    ) -> GetQuoteDetailResult:

        quote = (
            self.quote_repository
            .find_by_id(
                dto.quote_id
            )
        )

        if quote is None:
            raise QuoteNotFound()

        self.authorization.check_owner(
            quote.lead,
            dto.agent_id,
        )

        logger.info(
            "Détail du devis récupéré",
            extra={
                "quote_id": quote.id,
                "agent_id": dto.agent_id,
            },
        )

        return GetQuoteDetailResult(
            quote=quote
        )