from unittest.mock import Mock

import pytest

from modules.auth.domain.exceptions import Unauthorized
from modules.notifications.domain.exceptions import (
    NotificationNotFound,
)

from modules.notifications.application.dtos.mark_notification_read_dto import (
    MarkNotificationReadDTO,
)

from modules.notifications.application.use_cases.mark_notification_read import (
    MarkNotificationReadUseCase,
)


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(repository, unit_of_work):
    return MarkNotificationReadUseCase(
        repository=repository,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return MarkNotificationReadDTO(
        notification_id="notification-123",
        user_id="user-123",
    )


@pytest.fixture
def notification():
    notification = Mock()
    notification.id = "notification-123"
    notification.user_id = "user-123"
    notification.mark_as_read = Mock()
    return notification


def test_mark_notification_read_success(
    use_case,
    repository,
    unit_of_work,
    dto,
    notification,
):
    repository.get_by_id.return_value = notification

    result = use_case.execute(dto)

    repository.get_by_id.assert_called_once_with(
        "notification-123"
    )

    notification.mark_as_read.assert_called_once_with()

    repository.update.assert_called_once_with(
        notification
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    assert result.success is True
    assert result.message == "Notification marquée comme lue"


def test_mark_notification_read_raises_when_not_found(
    use_case,
    repository,
    unit_of_work,
    dto,
):
    repository.get_by_id.return_value = None

    with pytest.raises(NotificationNotFound):
        use_case.execute(dto)

    repository.delete.assert_not_called()
    repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_mark_notification_read_raises_when_user_is_not_owner(
    use_case,
    repository,
    unit_of_work,
    dto,
    notification,
):
    notification.user_id = "another-user"
    repository.get_by_id.return_value = notification

    with pytest.raises(Unauthorized):
        use_case.execute(dto)

    notification.mark_as_read.assert_not_called()
    repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_mark_notification_read_propagates_domain_error(
    use_case,
    repository,
    unit_of_work,
    dto,
    notification,
):
    repository.get_by_id.return_value = notification

    notification.mark_as_read.side_effect = RuntimeError(
        "Notification déjà lue"
    )

    with pytest.raises(
        RuntimeError,
        match="Notification déjà lue",
    ):
        use_case.execute(dto)

    notification.mark_as_read.assert_called_once_with()
    repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_mark_notification_read_rolls_back_when_update_fails(
    use_case,
    repository,
    unit_of_work,
    dto,
    notification,
):
    repository.get_by_id.return_value = notification
    repository.update.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(
        RuntimeError,
        match="Database error",
    ):
        use_case.execute(dto)

    notification.mark_as_read.assert_called_once_with()
    repository.update.assert_called_once_with(
        notification
    )
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_mark_notification_read_rolls_back_when_commit_fails(
    use_case,
    repository,
    unit_of_work,
    dto,
    notification,
):
    repository.get_by_id.return_value = notification
    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(dto)

    notification.mark_as_read.assert_called_once_with()
    repository.update.assert_called_once_with(
        notification
    )
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()
