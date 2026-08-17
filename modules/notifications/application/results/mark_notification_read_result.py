from dataclasses import dataclass


@dataclass(frozen=True)
class MarkNotificationReadResult:
    success: bool
    message: str