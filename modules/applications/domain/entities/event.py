from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from modules.applications.domain.enums import EventType


@dataclass
class Event:

    id: str

    # =====================================================
    # CONTENT
    # =====================================================

    type: EventType

    message: str

    event_metadata: dict[str, Any] | None = None

    # =====================================================
    # TIMESTAMP
    # =====================================================

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # =====================================================
    # RELATIONS / CONTEXT
    # =====================================================

    application_id: str | None = None

    test_drive_id: str | None = None

    user_id: str | None = None

    vehicle_id: str | None = None

    quote_id: str | None = None