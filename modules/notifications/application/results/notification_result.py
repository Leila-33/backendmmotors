from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NotificationResult:
    id: str
    title: str
    message: str
    type: str
    status: str
    created_at: datetime
    entity_type: str | None
    entity_id: str | None