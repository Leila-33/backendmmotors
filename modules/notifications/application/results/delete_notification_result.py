from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteNotificationResult:
    id: str
    success: bool
    message: str