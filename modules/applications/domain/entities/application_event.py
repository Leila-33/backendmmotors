from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ApplicationEvent:
    id: str
    application_id: str
    type: str
    message: str
    created_at: datetime
    user_id: Optional[str] = None