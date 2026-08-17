from dataclasses import dataclass


@dataclass
class RefuseQuoteDTO:

    quote_id: str
    customer_id: str
    reason: str
    comment: str | None = None