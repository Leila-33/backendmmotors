from dataclasses import dataclass


@dataclass
class DeleteQuoteDTO:

    quote_id: str

    agent_id: str