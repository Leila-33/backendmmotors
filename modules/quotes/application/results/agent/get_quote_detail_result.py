from modules.quotes.domain.entities.quote import Quote
from dataclasses import dataclass


@dataclass
class GetQuoteDetailResult:

    quote: Quote