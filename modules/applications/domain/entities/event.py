from dataclasses import dataclass
from datetime import datetime
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

    created_at: Optional[datetime] = None

    
    # =========================
    # RELATIONS CONTEXT
    # =========================

    application_id: Optional[str] = None

    test_drive_id: Optional[str] = None

    user_id: Optional[str] = None