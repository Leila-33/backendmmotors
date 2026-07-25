from fastapi import APIRouter, Depends
from modules.notifications.application.use_cases.get_notifications import (
    GetNotificationsUseCase
)
from modules.notifications.application.use_cases.get_unread_count import (
    GetUnreadCountUseCase
)
from modules.notifications.application.use_cases.mark_notification_read import MarkNotificationReadUseCase

from modules.notifications.api.schemas import (
    NotificationResponse,
    UnreadNotificationCountResponse,
    MarkNotificationReadResponse
)


from modules.notifications.api.schemas import DeleteNotificationResponse
from core.security.dependencies import get_current_user
from modules.notifications.api.dependencies import (
    get_get_notifications_usecase,
    get_mark_notification_read_usecase,
    get_unread_count_usecase,
    get_delete_notification_usecase
)

router = APIRouter(
    tags=["Notifications"]
)
# =========================
# GET MY NOTIFICATIONS
# =========================
@router.get(
    "/me",
    response_model=list[NotificationResponse]
)
def get_my_notifications(
    current_user = Depends(get_current_user),
    usecase: GetNotificationsUseCase = Depends(
        get_get_notifications_usecase
    ),
):

    return usecase.execute(
        user_id=current_user.id
    )


# =========================
# MARK AS READ
# =========================
@router.patch(
    "/{notification_id}/read",
    response_model=MarkNotificationReadResponse
)
def mark_notification_read(
    notification_id: str,
    current_user = Depends(get_current_user),
    use_case: MarkNotificationReadUseCase = Depends(
        get_mark_notification_read_usecase
    )
):

    return use_case.execute(
        notification_id,
        current_user.id
    )


# =========================
# COUNT UNREAD
# =========================
@router.get(
    "/unread/count",
    response_model=UnreadNotificationCountResponse
)
def get_unread_count(
    current_user = Depends(get_current_user),
    use_case: GetUnreadCountUseCase = Depends(
        get_unread_count_usecase
    )
):

    return use_case.execute(
        current_user.id
    )

# =========================
# DELETE
# =========================
@router.delete("/{notification_id}", response_model=DeleteNotificationResponse)
def delete_notification(
    notification_id: str,
    current_user=Depends(get_current_user),
    usecase=Depends(get_delete_notification_usecase)
):
    return usecase.execute(notification_id, current_user.id)