from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from modules.core.enums import (
    NotificationType,
    NotificationStatus
)


@dataclass
class Notification:

    id: str

    user_id: str

    # =====================
    # CONTENT
    # =====================
    title: str
    message: str

    # =====================
    # ENUMS
    # =====================
    type: NotificationType

    status: NotificationStatus = NotificationStatus.UNREAD

    # =====================
    # TIMESTAMP
    # =====================
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

     # =====================
    # CONTEXT (OPTIONAL)
    # =====================
    application_id: Optional[str] = None
    document_id: Optional[str] = None
    test_drive_id: Optional[str] = None