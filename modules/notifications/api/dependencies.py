from fastapi import Depends
# =========================
# CORE
# =========================

from core.database.dependencies import (
    get_unit_of_work,
)

# =========================
# REPOSITORY
# =========================
from modules.dependencies.dependencies import (
    get_notification_repository,
    get_websocket_manager
)

# =========================
# USE CASES
# =========================
from modules.notifications.application.use_cases.get_notifications import GetNotificationsUseCase
from modules.notifications.application.use_cases.mark_notification_read import MarkNotificationReadUseCase
from modules.notifications.application.use_cases.get_unread_count import GetUnreadCountUseCase
from modules.notifications.application.use_cases.delete_notification import DeleteNotificationUseCase

# =========================
# SERVICES
# =========================
from modules.notifications.application.services.notification_service import NotificationService

# =========================
# EXTERNAL
# =========================
from core.email.dependencies import get_email_service



def get_get_notifications_usecase(
    repository=Depends(get_notification_repository)
):
    return GetNotificationsUseCase(repository)


def get_mark_notification_read_usecase(
    repository=Depends(get_notification_repository),
    unit_of_work = Depends(get_unit_of_work)

):
    return MarkNotificationReadUseCase(
        repository=repository,
        unit_of_work=unit_of_work)


def get_unread_count_usecase(
    repository=Depends(get_notification_repository)
):
    return GetUnreadCountUseCase(repository)

def get_delete_notification_usecase(
    repository=Depends(get_notification_repository),
    unit_of_work = Depends(get_unit_of_work)

):

    return DeleteNotificationUseCase(
        repository=repository,
        unit_of_work = unit_of_work
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