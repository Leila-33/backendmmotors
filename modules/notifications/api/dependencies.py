# modules/notifications/infrastructure/dependencies.py

from fastapi import Depends

# =========================
# REPOSITORY
# =========================
from modules.core.infrastructure.dependencies import (
    get_notification_repository,
    get_websocket_manager
)

# =========================
# USE CASES
# =========================
from modules.notifications.application.uses_cases.get_notifications import GetNotificationsUseCase
from modules.notifications.application.uses_cases.mark_notification_read import MarkNotificationReadUseCase
from modules.notifications.application.uses_cases.get_unread_count import GetUnreadCountUseCase
from modules.notifications.application.uses_cases.delete_notification import DeleteNotificationUseCase

# =========================
# SERVICES
# =========================
from modules.notifications.application.services.notification_service import NotificationService

# =========================
# EXTERNAL
# =========================
from core.dependencies import get_email_service



def get_notifications_usecase(
    repository=Depends(get_notification_repository)
):
    return GetNotificationsUseCase(repository)


def get_mark_notification_read_usecase(
    repository=Depends(get_notification_repository)
):
    return MarkNotificationReadUseCase(repository)


def get_unread_count_usecase(
    repository=Depends(get_notification_repository)
):
    return GetUnreadCountUseCase(repository)

def get_delete_notification_usecase(
    repository=Depends(get_notification_repository),
):

    return DeleteNotificationUseCase(
        repository=repository
    )




def get_notification_service(

    notification_repo = Depends(get_notification_repository),

    email_service = Depends(get_email_service),

    websocket_manager = Depends(get_websocket_manager)

):

    return NotificationService(
        notification_repo=notification_repo,
        email_service=email_service,
        websocket_manager=websocket_manager
    )