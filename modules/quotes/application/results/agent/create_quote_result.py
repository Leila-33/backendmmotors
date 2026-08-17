from dataclasses import dataclass


@dataclass
class CreateQuoteResult:

    quote_id: str

    lead_id: str

    vehicle_id: str

    message: str