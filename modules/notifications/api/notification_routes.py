from fastapi import APIRouter, Depends

from modules.auth.domain.entities.user import User
from core.security.dependencies import get_current_user

# =========================
# USE CASES
# =========================

from modules.notifications.application.use_cases.get_notifications import (
    GetNotificationsUseCase,
)

from modules.notifications.application.use_cases.get_unread_count import (
    GetUnreadCountUseCase,
)

from modules.notifications.application.use_cases.mark_notification_read import (
    MarkNotificationReadUseCase,
)

from modules.notifications.application.use_cases.delete_notification import (
    DeleteNotificationUseCase,
)

# =========================
# DTO
# =========================

from modules.notifications.application.dtos.get_notifications_dto import (
    GetNotificationsDTO,
)

from modules.notifications.application.dtos.get_unread_count_dto import (
    GetUnreadCountDTO,
)

from modules.notifications.application.dtos.mark_notification_read_dto import (
    MarkNotificationReadDTO,
)

from modules.notifications.application.dtos.delete_notification_dto import (
    DeleteNotificationDTO,
)

# =========================
# DEPENDENCIES
# =========================

from modules.notifications.api.dependencies import (
    get_get_notifications_usecase,
    get_get_unread_count_usecase,
    get_mark_notification_read_usecase,
    get_delete_notification_usecase,
)

# =========================
# API SCHEMAS
# =========================

from modules.notifications.api.schemas import (
    GetNotificationsResponse,
    UnreadNotificationCountResponse,
    MarkNotificationReadResponse,
    DeleteNotificationResponse,
)

# =========================
# MAPPER
# =========================

from modules.notifications.infrastructure.mappers.notification_mapper import (
    NotificationMapper,
)


router = APIRouter(
    tags=["Notifications"],
)


# =====================================================
# GET MY NOTIFICATIONS
# =====================================================

@router.get(
    "/me",
    response_model=GetNotificationsResponse,
)
def get_my_notifications(
    current_user: User = Depends(
        get_current_user
    ),
    usecase: GetNotificationsUseCase = Depends(
        get_get_notifications_usecase
    ),
):

    dto = GetNotificationsDTO(
        user_id=current_user.id,
    )

    result = usecase.execute(
        dto
    )

    return NotificationMapper.to_list_response(
        result
    )


# =====================================================
# MARK AS READ
# =====================================================

@router.patch(
    "/{notification_id}/read",
    response_model=MarkNotificationReadResponse,
)
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: MarkNotificationReadUseCase = Depends(
        get_mark_notification_read_usecase
    ),
):

    dto = MarkNotificationReadDTO(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    result = await usecase.execute(
        dto
    )

    return NotificationMapper.to_mark_read_response(
        result
    )


# =====================================================
# COUNT UNREAD
# =====================================================

@router.get(
    "/unread-count",
    response_model=UnreadNotificationCountResponse,
)
def get_unread_count(
    current_user: User = Depends(
        get_current_user
    ),
    usecase: GetUnreadCountUseCase = Depends(
        get_get_unread_count_usecase
    ),
):

    dto = GetUnreadCountDTO(
        user_id=current_user.id,
    )

    result = usecase.execute(
        dto
    )

    return NotificationMapper.to_unread_count_response(
        result
    )


# =====================================================
# DELETE
# =====================================================

@router.delete(
    "/{notification_id}",
    response_model=DeleteNotificationResponse,
)
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: DeleteNotificationUseCase = Depends(
        get_delete_notification_usecase
    ),
):

    dto = DeleteNotificationDTO(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    result = await usecase.execute(
        dto
    )

    return NotificationMapper.to_delete_response(
        result
    )