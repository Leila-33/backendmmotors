from dataclasses import dataclass
from datetime import datetime


@dataclass
class ApplicationEvent:
    id: str
    application_id: str
    type: str  # CREATED, DOCUMENT_ADDED, SUBMITTED, APPROVED...
    message: str
    created_at: datetime