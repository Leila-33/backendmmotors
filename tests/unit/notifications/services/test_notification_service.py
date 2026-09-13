from unittest.mock import AsyncMock, Mock, patch

import pytest

from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationStatus,
    NotificationType,
)
from modules.notifications.domain.exceptions import (
    InvalidNotificationEntityType,
    InvalidNotificationType,
)
from modules.notifications.application.services.notification_service import (
    NotificationService,
)


@pytest.fixture
def notification_repo():
    return Mock()


@pytest.fixture
def email_service():
    return Mock()


@pytest.fixture
def websocket_manager():
    manager = Mock()
    manager.send = AsyncMock()
    return manager


@pytest.fixture
def service(
    notification_repo,
    email_service,
    websocket_manager,
):
    return NotificationService(
        notification_repo=notification_repo,
        email_service=email_service,
        websocket_manager=websocket_manager,
    )


@pytest.mark.asyncio
async def test_send_creates_notification_with_enum_values(
    service,
    notification_repo,
    email_service,
    websocket_manager,
):
    result = await service.send(
        user_id="user-123",
        title="Devis envoyé",
        message="Votre devis a été envoyé.",
        notif_type=NotificationType.QUOTE_SENT,
        entity_type=NotificationEntityType.QUOTE,
        entity_id="quote-123",
    )

    assert result.user_id == "user-123"
    assert result.title == "Devis envoyé"
    assert result.message == "Votre devis a été envoyé."
    assert result.type == NotificationType.QUOTE_SENT
    assert result.status == NotificationStatus.UNREAD
    assert result.entity_type == NotificationEntityType.QUOTE
    assert result.entity_id == "quote-123"
    assert result.id
    assert result.created_at.tzinfo is not None

    notification_repo.save.assert_called_once_with(result)
    email_service.send.assert_not_called()
    websocket_manager.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_normalizes_notification_type_from_string(
    service,
    notification_repo,
):
    with patch(
        "modules.notifications.application.services.notification_service.uuid4",
        return_value="notification-123",
    ):
        result = await service.send(
            user_id="user-123",
            title="Test",
            message="Message",
            notif_type=NotificationType.QUOTE_SENT.value,
        )

    assert result.id == "notification-123"
    assert result.type == NotificationType.QUOTE_SENT
    assert result.status == NotificationStatus.UNREAD

    notification_repo.save.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_send_raises_for_invalid_notification_type(
    service,
    notification_repo,
):
    with pytest.raises(InvalidNotificationType):
        await service.send(
            user_id="user-123",
            title="Test",
            message="Message",
            notif_type="INVALID_TYPE",
        )

    notification_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_send_raises_for_invalid_entity_type(
    service,
    notification_repo,
):
    with pytest.raises(InvalidNotificationEntityType):
        await service.send(
            user_id="user-123",
            title="Test",
            message="Message",
            notif_type=NotificationType.QUOTE_SENT,
            entity_type="INVALID_ENTITY",
        )

    notification_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_send_sends_email_when_email_is_provided(
    service,
    notification_repo,
    email_service,
):
    result = await service.send(
        user_id="user-123",
        title="Devis envoyé",
        message="Votre devis a été envoyé.",
        notif_type=NotificationType.QUOTE_SENT,
        entity_type=NotificationEntityType.QUOTE,
        entity_id="quote-123",
        email="customer@example.com",
    )

    notification_repo.save.assert_called_once_with(result)

    email_service.send.assert_called_once_with(
        to="customer@example.com",
        subject="Devis envoyé",
        body="Votre devis a été envoyé.",
    )


@pytest.mark.asyncio
async def test_send_sends_websocket_notification(
    service,
    notification_repo,
    websocket_manager,
):
    result = await service.send(
        user_id="user-123",
        title="Notification",
        message="Message",
        notif_type=NotificationType.QUOTE_SENT,
        entity_type=NotificationEntityType.QUOTE,
        entity_id="quote-123",
    )

    websocket_manager.send.assert_awaited_once_with(
        "user-123",
        {
            "id": result.id,
            "title": "Notification",
            "message": "Message",
            "type": NotificationType.QUOTE_SENT.value,
            "status": NotificationStatus.UNREAD.value,
            "entity_type": NotificationEntityType.QUOTE.value,
            "entity_id": "quote-123",
            "created_at": result.created_at.isoformat(),
        },
    )


@pytest.mark.asyncio
async def test_send_does_not_send_email_without_email(
    service,
    notification_repo,
    email_service,
):
    result = await service.send(
        user_id="user-123",
        title="Notification",
        message="Message",
        notif_type=NotificationType.QUOTE_SENT,
        entity_type=NotificationEntityType.QUOTE,
        entity_id="quote-123",
    )

    notification_repo.save.assert_called_once_with(result)
    email_service.send.assert_not_called()