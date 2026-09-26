from dataclasses import dataclass

@dataclass
class RefuseQuoteResult:

    quote_id: str
    message: str