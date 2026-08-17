from dataclasses import dataclass


@dataclass
class SendQuoteDTO:

    quote_id: str

    agent_id: str