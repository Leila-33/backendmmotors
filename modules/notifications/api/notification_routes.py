from fastapi import APIRouter, Depends

router = APIRouter(
    tags=["Notifications"]
)

from core.security.dependencies import get_current_user
from modules.notifications.api.dependencies import (
    get_notifications_usecase,
    get_mark_notification_read_usecase,
    get_unread_count_usecase,
    get_delete_notification_usecase
)
# =========================
# GET MY NOTIFICATIONS
# =========================
@router.get("/me")
def get_my_notifications(
    current_user=Depends(get_current_user),
    usecase=Depends(get_notifications_usecase)
):
    return usecase.execute(current_user.id)


# =========================
# MARK AS READ
# =========================
@router.post("/{notification_id}/read")
def mark_as_read(
    notification_id: str,
    current_user=Depends(get_current_user),
    usecase=Depends(get_mark_notification_read_usecase)
):
    return usecase.execute(notification_id, current_user.id)


# =========================
# COUNT UNREAD
# =========================
@router.get("/me/unread-count")
def unread_count(
    current_user=Depends(get_current_user),
    usecase=Depends(get_unread_count_usecase)
):
    return {"count": usecase.execute(current_user.id)}


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: str,
    current_user=Depends(get_current_user),
    usecase=Depends(get_delete_notification_usecase)
):
    return usecase.execute(notification_id, current_user.id)