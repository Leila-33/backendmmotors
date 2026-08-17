from dataclasses import dataclass
from modules.quotes.domain.entities.quote import Quote


@dataclass
class GetCustomerQuoteDetailResult:

    quote: Quote
    application_id: str | None
