from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# delete notifications
class DeleteNotificationResponse(BaseModel):

    id: str

    success: bool

    message: str

# get notifications
class NotificationResponse(BaseModel):

    id: str

    title: str

    message: str

    type: str

    status: str

    created_at: datetime

    entity_type: Optional[str] = None

    entity_id: Optional[str] = None



# get unread count
class UnreadNotificationCountResponse(BaseModel):

    count: int

# mark notification read
class MarkNotificationReadResponse(BaseModel):

    success: bool

    message: str