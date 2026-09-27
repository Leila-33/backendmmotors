from modules.quotes.domain.exceptions import (
    QuoteNotFound,
    QuoteNotAvailableForCustomer,
)

from modules.quotes.application.dtos.customer_quote_dto import (
    CustomerQuoteDTO,
)

from modules.quotes.application.results.get_customer_quote_detail_result import (
    GetCustomerQuoteDetailResult,
)


class GetCustomerQuoteDetailUseCase:
    """
    Récupère le détail d'un devis accessible au client connecté
    et indique si un dossier a déjà été créé à partir de celui-ci.
    """
    def __init__(
        self,
        quote_repository,
        application_repository,
    ):
        self.quote_repository = quote_repository
        self.application_repository = application_repository

    def execute(
        self,
        dto: CustomerQuoteDTO,
    ) -> GetCustomerQuoteDetailResult:

        # =========================
        # QUOTE
        # =========================

        quote = (
            self.quote_repository
            .find_customer_quote_by_id(
                dto.quote_id,
                dto.customer_id,
            )
        )

        if quote is None:
            raise QuoteNotFound()

        # =========================
        # CUSTOMER ACCESS
        # =========================

        if not quote.can_be_viewed_by_customer():
            raise QuoteNotAvailableForCustomer()

        # =========================
        # APPLICATION
        # =========================

        application = (
            self.application_repository
            .find_by_quote_id(
                quote.id
            )
        )

        # =========================
        # RESULT
        # =========================

        return GetCustomerQuoteDetailResult(
            quote=quote,
            application_id=(
                application.id
                if application
                else None
            ),
        )