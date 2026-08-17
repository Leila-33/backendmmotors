from dataclasses import dataclass

@dataclass
class AcceptQuoteResult:

    quote_id: str
    application_id: str
    message: str