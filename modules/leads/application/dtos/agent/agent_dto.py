from dataclasses import dataclass


@dataclass(frozen=True)
class AgentDTO:
    agent_id: str