from modules.notifications.infrastructure.repositories.notification_repository_sql import NotificationRepositorySQL
from infrastructure.db.dependencies import get_db

from fastapi import Depends

from modules.notifications.infrastructure.repositories.notification_repository_sql import NotificationRepositorySQL

from modules.notifications.application.uses_cases.get_notifications import GetNotificationsUseCase
from modules.notifications.application.uses_cases.mark_notification_read import MarkNotificationReadUseCase
from modules.notifications.application.uses_cases.get_unread_count import GetUnreadCountUseCase

def get_notification_repository(
    db = Depends(get_db)
):
    return NotificationRepositorySQL(db)


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
from modules.notifications.application.uses_cases.delete_notification import DeleteNotificationUseCase

def get_delete_notification_usecase(
    repository=Depends(get_notification_repository),
):

    return DeleteNotificationUseCase(
        repository=repository
    )


from modules.notifications.api.notifications_ws_router import manager
from modules.notifications.application.services.notification_service import NotificationService

def get_websocket_manager():
    return manager

from modules.notifications.application.services.notification_service import NotificationService

from modules.notifications.api.dependencies import (
    get_notification_repository
)

from core.dependencies import (
    get_email_service
)

def get_notification_service(

    notification_repo = Depends(get_notification_repository),

    email_service = Depends(get_email_service),

    websocket_manager = Depends(get_websocket_manager)  # ⭐ AJOUT

):

    return NotificationService(
        notification_repo=notification_repo,
        email_service=email_service,
        websocket_manager=websocket_manager
    )