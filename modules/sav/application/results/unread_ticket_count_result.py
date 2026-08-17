from dataclasses import dataclass


@dataclass(frozen=True)
class UnreadTicketCountResult:
    count: int