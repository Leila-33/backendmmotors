import logging

from modules.quotes.domain.exceptions import (
    QuoteNotFound,
)

from modules.quotes.application.dtos.agent.quote_agent_dto import (
    QuoteAgentDTO,
)

from modules.quotes.application.results.agent.get_quote_detail_result import (
    GetQuoteDetailResult,
)


logger = logging.getLogger(__name__)


class GetQuoteDetailUseCase:
    """
    Récupère le détail d'un devis après vérification
    des droits d'accès de l'agent.
    """
    def __init__(
        self,
        quote_repository,
        authorization,
    ):

        self.quote_repository = quote_repository
        self.authorization = authorization

    def execute(
        self,
        dto: QuoteAgentDTO,
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