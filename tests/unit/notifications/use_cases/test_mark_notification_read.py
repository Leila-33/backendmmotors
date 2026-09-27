import pytest
from unittest.mock import AsyncMock, Mock

from modules.notifications.application.dtos.mark_notification_read_dto import (
    MarkNotificationReadDTO,
)
from modules.notifications.application.results.mark_notification_read_result import (
    MarkNotificationReadResult,
)
from modules.notifications.application.use_cases.mark_notification_read import (
    MarkNotificationReadUseCase,
)
from modules.notifications.domain.exceptions import (
    NotificationNotFound,
)
from modules.auth.domain.exceptions import Unauthorized


# ============================================================
# HELPERS
# ============================================================


def make_notification(
    *,
    notification_id: str = "notification-1",
    user_id: str = "user-1",
):
    notification = Mock(
        id=notification_id,
        user_id=user_id,
    )

    return notification


def make_dto(
    *,
    notification_id: str = "notification-1",
    user_id: str = "user-1",
):
    return MarkNotificationReadDTO(
        notification_id=notification_id,
        user_id=user_id,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def notification_service():
    service = Mock()
    service.send_update = AsyncMock()
    return service


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    repository,
    notification_service,
    unit_of_work,
):
    return MarkNotificationReadUseCase(
        repository=repository,
        notification_service=notification_service,
        unit_of_work=unit_of_work,
    )


# ============================================================
# NOTIFICATION NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_notification_not_found(
    use_case,
    repository,
    unit_of_work,
):
    repository.get_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(NotificationNotFound):
        await use_case.execute(dto)

    repository.get_by_id.assert_called_once_with(
        "notification-1"
    )

    repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# SECURITY
# ============================================================


@pytest.mark.asyncio
async def test_user_cannot_mark_another_users_notification_as_read(
    use_case,
    repository,
    unit_of_work,
):
    notification = make_notification(
        user_id="owner-1",
    )

    repository.get_by_id.return_value = notification

    dto = make_dto(
        user_id="another-user",
    )

    with pytest.raises(Unauthorized):
        await use_case.execute(dto)

    repository.update.assert_not_called()

    notification.mark_as_read.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_user_can_mark_own_notification_as_read(
    use_case,
    repository,
    unit_of_work,
):
    notification = make_notification(
        user_id="user-1",
    )

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 2

    dto = make_dto(
        user_id="user-1",
    )

    await use_case.execute(dto)

    notification.mark_as_read.assert_called_once()

    repository.update.assert_called_once_with(
        notification
    )

    unit_of_work.commit.assert_called_once()


# ============================================================
# DOMAIN ACTION
# ============================================================


@pytest.mark.asyncio
async def test_notification_is_marked_as_read(
    use_case,
    repository,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 0

    dto = make_dto()

    await use_case.execute(dto)

    notification.mark_as_read.assert_called_once()


# ============================================================
# UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_notification_is_updated(
    use_case,
    repository,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 0

    dto = make_dto()

    await use_case.execute(dto)

    repository.update.assert_called_once_with(
        notification
    )


# ============================================================
# COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_commit_is_called(
    use_case,
    repository,
    unit_of_work,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 0

    dto = make_dto()

    await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# UNREAD COUNT
# ============================================================


@pytest.mark.asyncio
async def test_unread_count_is_loaded_after_commit(
    use_case,
    repository,
    unit_of_work,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 3

    dto = make_dto()

    await use_case.execute(dto)

    repository.count_unread.assert_called_once_with(
        "user-1"
    )

    unit_of_work.commit.assert_called_once()


@pytest.mark.asyncio
async def test_unread_count_can_be_zero(
    use_case,
    repository,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 0

    dto = make_dto()

    await use_case.execute(dto)

    repository.count_unread.assert_called_once_with(
        "user-1"
    )


# ============================================================
# NOTIFICATION UPDATE / WEBSOCKET
# ============================================================


@pytest.mark.asyncio
async def test_unread_count_update_is_sent(
    use_case,
    repository,
    notification_service,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 3

    dto = make_dto()

    await use_case.execute(dto)

    notification_service.send_update.assert_awaited_once_with(
        user_id="user-1",
        payload={
            "type": "UNREAD_NOTIFICATIONS_UPDATED",
            "count": 3,
        },
    )


@pytest.mark.asyncio
async def test_unread_count_update_is_sent_with_zero(
    use_case,
    repository,
    notification_service,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 0

    dto = make_dto()

    await use_case.execute(dto)

    notification_service.send_update.assert_awaited_once_with(
        user_id="user-1",
        payload={
            "type": "UNREAD_NOTIFICATIONS_UPDATED",
            "count": 0,
        },
    )


# ============================================================
# RESULT
# ============================================================


@pytest.mark.asyncio
async def test_mark_notification_read_result_is_returned(
    use_case,
    repository,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 0

    dto = make_dto()

    result = await use_case.execute(dto)

    assert isinstance(
        result,
        MarkNotificationReadResult,
    )

    assert result.success is True
    assert result.message == (
        "Notification marquée comme lue"
    )


# ============================================================
# ROLLBACK / ERRORS
# ============================================================


@pytest.mark.asyncio
async def test_mark_as_read_error_rolls_back(
    use_case,
    repository,
    unit_of_work,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification

    notification.mark_as_read.side_effect = RuntimeError(
        "mark as read error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="mark as read error",
    ):
        await use_case.execute(dto)

    notification.mark_as_read.assert_called_once()

    repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_update_error_rolls_back(
    use_case,
    repository,
    unit_of_work,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification

    repository.update.side_effect = RuntimeError(
        "update error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        await use_case.execute(dto)

    notification.mark_as_read.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_commit_error_rolls_back(
    use_case,
    repository,
    unit_of_work,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        await use_case.execute(dto)

    notification.mark_as_read.assert_called_once()
    repository.update.assert_called_once_with(
        notification
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_count_unread_error_rolls_back(
    use_case,
    repository,
    unit_of_work,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification

    repository.count_unread.side_effect = RuntimeError(
        "count unread error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="count unread error",
    ):
        await use_case.execute(dto)

    notification.mark_as_read.assert_called_once()
    repository.update.assert_called_once_with(
        notification
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_send_update_error_rolls_back(
    use_case,
    repository,
    notification_service,
    unit_of_work,
):
    notification = make_notification()

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 2

    notification_service.send_update.side_effect = (
        RuntimeError("send update error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="send update error",
    ):
        await use_case.execute(dto)

    notification.mark_as_read.assert_called_once()
    repository.update.assert_called_once_with(
        notification
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# COMPLETE SUCCESS FLOW
# ============================================================


@pytest.mark.asyncio
async def test_mark_notification_read_complete_flow(
    use_case,
    repository,
    notification_service,
    unit_of_work,
):
    notification = make_notification(
        notification_id="notification-42",
        user_id="user-42",
    )

    repository.get_by_id.return_value = notification
    repository.count_unread.return_value = 5

    dto = make_dto(
        notification_id="notification-42",
        user_id="user-42",
    )

    result = await use_case.execute(dto)

    repository.get_by_id.assert_called_once_with(
        "notification-42"
    )

    notification.mark_as_read.assert_called_once()

    repository.update.assert_called_once_with(
        notification
    )

    unit_of_work.commit.assert_called_once()

    repository.count_unread.assert_called_once_with(
        "user-42"
    )

    notification_service.send_update.assert_awaited_once_with(
        user_id="user-42",
        payload={
            "type": "UNREAD_NOTIFICATIONS_UPDATED",
            "count": 5,
        },
    )

    assert isinstance(
        result,
        MarkNotificationReadResult,
    )

    assert result.success is True
    assert result.message == (
        "Notification marquée comme lue"
    )