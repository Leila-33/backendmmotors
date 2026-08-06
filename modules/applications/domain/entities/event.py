from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from modules.applications.domain.enums import EventType

@dataclass
class Event:

    id: str

    # =========================
    # CONTENT
    # =========================

    type: EventType

    message: str

    event_metadata: Optional[dict] = None

    # =========================
    # TIMESTAMP
    # =========================

    created_at: datetime = field(
            default_factory=lambda: datetime.now(timezone.utc)
        )
    
    # =========================
    # RELATIONS CONTEXT
    # =========================

    application_id: Optional[str] = None

    test_drive_id: Optional[str] = None

    user_id: Optional[str] = None

    vehicle_id: Optional[str] = None

    quote_id: Optional[str] = None
