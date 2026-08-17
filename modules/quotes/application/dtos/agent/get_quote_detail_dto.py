from dataclasses import dataclass


@dataclass
class GetQuoteDetailDTO:

    quote_id: str

    agent_id: str