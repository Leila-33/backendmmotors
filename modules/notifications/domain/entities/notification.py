from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    APPLICATION_APPROVED = "application_approved"
    APPLICATION_REJECTED = "application_rejected"
    APPLICATION_SUBMITTED = "application_submitted"
    DOCUMENT_APPROVED = "application_approved"
    DOCUMENT_REJECTED = "document_rejected"


class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"


@dataclass
class Notification:
    id: str
    user_id: str
    application_id: str

    title: str
    message: str

    type: NotificationType

    status: NotificationStatus = NotificationStatus.UNREAD
    is_read: bool = False

    created_at: datetime = None