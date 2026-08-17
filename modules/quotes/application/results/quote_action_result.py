from dataclasses import dataclass


@dataclass
class QuoteActionResult:
    quote_id: str
    message: str