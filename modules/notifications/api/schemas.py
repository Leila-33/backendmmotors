from datetime import datetime

from pydantic import BaseModel, Field


# =====================================================
# NOTIFICATION
# =====================================================

class NotificationResponse(BaseModel):

    id: str

    title: str

    message: str

    type: str

    status: str

    created_at: datetime

    entity_type: str | None = None

    entity_id: str | None = None


# =====================================================
# GET NOTIFICATIONS
# =====================================================

class GetNotificationsResponse(BaseModel):

    notifications: list[NotificationResponse] = Field(
        default_factory=list
    )


# =====================================================
# UNREAD COUNT
# =====================================================

class UnreadNotificationCountResponse(BaseModel):

    count: int


# =====================================================
# MARK AS READ
# =====================================================

class MarkNotificationReadResponse(BaseModel):

    success: bool

    message: str


# =====================================================
# DELETE
# =====================================================

class DeleteNotificationResponse(BaseModel):

    id: str

    success: bool

    message: str