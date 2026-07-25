from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from modules.notifications.domain.enums import(
    NotificationType,
    NotificationStatus,
    NotificationEntityType
)


from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


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

    status: NotificationStatus = (
        NotificationStatus.UNREAD
    )


    # =====================
    # TIMESTAMP
    # =====================

    created_at: datetime = field(
        default_factory=lambda:
            datetime.now(timezone.utc)
    )

    # =====================
    # CONTEXT
    # =====================

    entity_type: Optional[NotificationEntityType] = None

    entity_id: Optional[str] = None

    
    def mark_as_read(self):

        if self.status == NotificationStatus.READ:
            return

        self.status = NotificationStatus.READ