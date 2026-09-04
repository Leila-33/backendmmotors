from dataclasses import dataclass


@dataclass(frozen=True)
class QuoteAgentDTO:
    quote_id: str
    agent_id: str