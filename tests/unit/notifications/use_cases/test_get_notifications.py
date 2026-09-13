from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from modules.notifications.application.dtos.get_notifications_dto import (
    GetNotificationsDTO,
)
from modules.notifications.application.use_cases.get_notifications import (
    GetNotificationsUseCase,
)


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def use_case(repository):
    return GetNotificationsUseCase(
        notification_repository=repository,
    )


@pytest.fixture
def dto():
    return GetNotificationsDTO(
        user_id="user-123",
    )


def test_get_notifications_returns_notifications(
    use_case,
    repository,
    dto,
):
    created_at = datetime.now(timezone.utc)

    notification = Mock()
    notification.id = "notification-123"
    notification.title = "Nouveau lead"
    notification.message = "Un nouveau lead vous a été attribué."
    notification.type.value = "LEAD_ASSIGNED"
    notification.status.value = "UNREAD"
    notification.created_at = created_at
    notification.entity_type.value = "LEAD"
    notification.entity_id = "lead-123"

    repository.get_by_user.return_value = [notification]

    result = use_case.execute(dto)

    repository.get_by_user.assert_called_once_with(
        "user-123"
    )

    assert len(result.items) == 1

    item = result.items[0]

    assert item.id == "notification-123"
    assert item.title == "Nouveau lead"
    assert item.message == "Un nouveau lead vous a été attribué."
    assert item.type == "LEAD_ASSIGNED"
    assert item.status == "UNREAD"
    assert item.created_at == created_at
    assert item.entity_type == "LEAD"
    assert item.entity_id == "lead-123"


def test_get_notifications_returns_empty_list_when_no_notifications(
    use_case,
    repository,
    dto,
):
    repository.get_by_user.return_value = []

    result = use_case.execute(dto)

    repository.get_by_user.assert_called_once_with(
        "user-123"
    )

    assert result.items == []


def test_get_notifications_handles_notification_without_entity_type(
    use_case,
    repository,
    dto,
):
    notification = Mock()

    notification.id = "notification-123"
    notification.title = "Information"
    notification.message = "Votre demande a été mise à jour."
    notification.type.value = "APPLICATION_UPDATED"
    notification.status.value = "READ"
    notification.created_at = datetime.now(timezone.utc)
    notification.entity_type = None
    notification.entity_id = None

    repository.get_by_user.return_value = [notification]

    result = use_case.execute(dto)

    item = result.items[0]

    assert item.entity_type is None
    assert item.entity_id is None


def test_get_notifications_transforms_multiple_notifications(
    use_case,
    repository,
    dto,
):
    notification_1 = Mock()
    notification_1.id = "notification-1"
    notification_1.title = "Notification 1"
    notification_1.message = "Message 1"
    notification_1.type.value = "LEAD_ASSIGNED"
    notification_1.status.value = "UNREAD"
    notification_1.created_at = datetime.now(timezone.utc)
    notification_1.entity_type.value = "LEAD"
    notification_1.entity_id = "lead-1"

    notification_2 = Mock()
    notification_2.id = "notification-2"
    notification_2.title = "Notification 2"
    notification_2.message = "Message 2"
    notification_2.type.value = "QUOTE_CREATED"
    notification_2.status.value = "READ"
    notification_2.created_at = datetime.now(timezone.utc)
    notification_2.entity_type.value = "QUOTE"
    notification_2.entity_id = "quote-1"

    repository.get_by_user.return_value = [
        notification_1,
        notification_2,
    ]

    result = use_case.execute(dto)

    assert len(result.items) == 2

    assert result.items[0].id == "notification-1"
    assert result.items[0].type == "LEAD_ASSIGNED"

    assert result.items[1].id == "notification-2"
    assert result.items[1].type == "QUOTE_CREATED"


def test_get_notifications_propagates_repository_error(
    use_case,
    repository,
    dto,
):
    repository.get_by_user.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    repository.get_by_user.assert_called_once_with(
        "user-123"
    )
