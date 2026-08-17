from dataclasses import dataclass


@dataclass(frozen=True)
class GetUnreadCountResult:
    count: int