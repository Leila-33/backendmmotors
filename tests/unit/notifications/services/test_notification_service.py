import pytest
from unittest.mock import AsyncMock, Mock

from modules.notifications.application.services.notification_service import (
    NotificationService,
)
from modules.notifications.domain.entities.notification import (
    Notification,
)
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationStatus,
    NotificationType,
)
from modules.notifications.domain.exceptions import (
    InvalidNotificationEntityType,
    InvalidNotificationType,
)


# ============================================================
# HELPERS
# ============================================================


def get_notification_type():
    """
    Retourne un type de notification réellement défini
    dans l'enum du projet.
    """
    return next(iter(NotificationType))


def get_notification_entity_type():
    """
    Retourne un type d'entité réellement défini
    dans l'enum du projet.
    """
    return next(iter(NotificationEntityType))


# ============================================================
# FIXTURES
# ============================================================


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
):
    return NotificationService(
        notification_repo=notification_repo,
        email_service=email_service,
    )


@pytest.fixture
def service_with_websocket(
    notification_repo,
    email_service,
    websocket_manager,
):
    return NotificationService(
        notification_repo=notification_repo,
        email_service=email_service,
        websocket_manager=websocket_manager,
    )


# ============================================================
# SEND NOTIFICATION
# ============================================================


@pytest.mark.asyncio
async def test_send_notification_creates_notification(
    service,
    notification_repo,
):
    notif_type = get_notification_type()

    result = await service.send(
        user_id="user-1",
        title="Test notification",
        message="Test message",
        notif_type=notif_type,
    )

    assert isinstance(
        result,
        Notification,
    )

    assert result.user_id == "user-1"
    assert result.title == "Test notification"
    assert result.message == "Test message"
    assert result.type == notif_type
    assert result.status == NotificationStatus.UNREAD
    assert result.entity_type is None
    assert result.entity_id is None
    assert result.id is not None
    assert result.created_at is not None
    assert result.created_at.tzinfo is not None

    notification_repo.save.assert_called_once_with(
        result
    )


# ============================================================
# SEND — NOTIFICATION TYPE ENUM
# ============================================================


@pytest.mark.asyncio
async def test_send_accepts_notification_type_enum(
    service,
    notification_repo,
):
    notif_type = get_notification_type()

    result = await service.send(
        user_id="user-1",
        title="Title",
        message="Message",
        notif_type=notif_type,
    )

    assert result.type == notif_type

    notification_repo.save.assert_called_once_with(
        result
    )


# ============================================================
# SEND — NOTIFICATION TYPE STRING
# ============================================================


@pytest.mark.asyncio
async def test_send_normalizes_notification_type_string(
    service,
    notification_repo,
):
    notif_type = get_notification_type()

    result = await service.send(
        user_id="user-1",
        title="Title",
        message="Message",
        notif_type=notif_type.value,
    )

    assert result.type == notif_type

    notification_repo.save.assert_called_once_with(
        result
    )


# ============================================================
# SEND — INVALID NOTIFICATION TYPE
# ============================================================


@pytest.mark.asyncio
async def test_send_rejects_invalid_notification_type(
    service,
    notification_repo,
):
    with pytest.raises(
        InvalidNotificationType
    ):
        await service.send(
            user_id="user-1",
            title="Title",
            message="Message",
            notif_type="INVALID_NOTIFICATION_TYPE",
        )

    notification_repo.save.assert_not_called()


# ============================================================
# SEND — ENTITY TYPE ENUM
# ============================================================


@pytest.mark.asyncio
async def test_send_accepts_entity_type_enum(
    service,
    notification_repo,
):
    notif_type = get_notification_type()
    entity_type = get_notification_entity_type()

    result = await service.send(
        user_id="user-1",
        title="Title",
        message="Message",
        notif_type=notif_type,
        entity_type=entity_type,
        entity_id="entity-1",
    )

    assert result.entity_type == entity_type
    assert result.entity_id == "entity-1"

    notification_repo.save.assert_called_once_with(
        result
    )


# ============================================================
# SEND — ENTITY TYPE STRING
# ============================================================


@pytest.mark.asyncio
async def test_send_normalizes_entity_type_string(
    service,
    notification_repo,
):
    notif_type = get_notification_type()
    entity_type = get_notification_entity_type()

    result = await service.send(
        user_id="user-1",
        title="Title",
        message="Message",
        notif_type=notif_type,
        entity_type=entity_type.value,
        entity_id="entity-1",
    )

    assert result.entity_type == entity_type
    assert result.entity_id == "entity-1"

    notification_repo.save.assert_called_once_with(
        result
    )


# ============================================================
# SEND — INVALID ENTITY TYPE
# ============================================================


@pytest.mark.asyncio
async def test_send_rejects_invalid_entity_type(
    service,
    notification_repo,
):
    notif_type = get_notification_type()

    with pytest.raises(
        InvalidNotificationEntityType
    ):
        await service.send(
            user_id="user-1",
            title="Title",
            message="Message",
            notif_type=notif_type,
            entity_type="INVALID_ENTITY_TYPE",
        )

    notification_repo.save.assert_not_called()


# ============================================================
# SEND — EMAIL
# ============================================================


@pytest.mark.asyncio
async def test_send_sends_email_when_email_is_provided(
    service,
    notification_repo,
    email_service,
):
    notif_type = get_notification_type()

    result = await service.send(
        user_id="user-1",
        title="Nouvelle notification",
        message="Contenu de la notification",
        notif_type=notif_type,
        email="customer@example.com",
    )

    notification_repo.save.assert_called_once_with(
        result
    )

    email_service.send.assert_called_once_with(
        to="customer@example.com",
        subject="Nouvelle notification",
        body="Contenu de la notification",
    )


# ============================================================
# SEND — NO EMAIL
# ============================================================


@pytest.mark.asyncio
async def test_send_does_not_send_email_when_email_is_none(
    service,
    notification_repo,
    email_service,
):
    notif_type = get_notification_type()

    result = await service.send(
        user_id="user-1",
        title="Title",
        message="Message",
        notif_type=notif_type,
        email=None,
    )

    notification_repo.save.assert_called_once_with(
        result
    )

    email_service.send.assert_not_called()


# ============================================================
# SEND — WEBSOCKET
# ============================================================


@pytest.mark.asyncio
async def test_send_sends_websocket_notification(
    service_with_websocket,
    notification_repo,
    websocket_manager,
):
    notif_type = get_notification_type()
    entity_type = get_notification_entity_type()

    result = await service_with_websocket.send(
        user_id="user-1",
        title="Title",
        message="Message",
        notif_type=notif_type,
        entity_type=entity_type,
        entity_id="entity-1",
    )

    websocket_manager.send.assert_awaited_once()

    args = websocket_manager.send.await_args.args

    assert args[0] == "user-1"

    payload = args[1]

    assert payload["id"] == result.id
    assert payload["title"] == "Title"
    assert payload["message"] == "Message"
    assert payload["type"] == notif_type.value
    assert payload["status"] == NotificationStatus.UNREAD.value
    assert payload["entity_type"] == entity_type.value
    assert payload["entity_id"] == "entity-1"
    assert payload["created_at"] == (
        result.created_at.isoformat()
    )


# ============================================================
# SEND — NO WEBSOCKET
# ============================================================


@pytest.mark.asyncio
async def test_send_does_not_use_websocket_when_not_configured(
    service,
    notification_repo,
    email_service,
):
    notif_type = get_notification_type()

    result = await service.send(
        user_id="user-1",
        title="Title",
        message="Message",
        notif_type=notif_type,
    )

    assert isinstance(
        result,
        Notification,
    )

    notification_repo.save.assert_called_once_with(
        result
    )

    email_service.send.assert_not_called()


# ============================================================
# SEND — COMPLETE FLOW
# ============================================================


@pytest.mark.asyncio
async def test_send_complete_flow(
    service_with_websocket,
    notification_repo,
    email_service,
    websocket_manager,
):
    notif_type = get_notification_type()
    entity_type = get_notification_entity_type()

    result = await service_with_websocket.send(
        user_id="user-42",
        title="Nouvelle offre commerciale",
        message="Votre devis est disponible.",
        notif_type=notif_type,
        email="customer@example.com",
        entity_type=entity_type,
        entity_id="quote-42",
    )

    # Notification
    assert isinstance(
        result,
        Notification,
    )

    assert result.id is not None
    assert result.user_id == "user-42"
    assert result.title == "Nouvelle offre commerciale"
    assert result.message == (
        "Votre devis est disponible."
    )
    assert result.type == notif_type
    assert result.status == NotificationStatus.UNREAD
    assert result.entity_type == entity_type
    assert result.entity_id == "quote-42"

    # Repository
    notification_repo.save.assert_called_once_with(
        result
    )

    # Email
    email_service.send.assert_called_once_with(
        to="customer@example.com",
        subject="Nouvelle offre commerciale",
        body="Votre devis est disponible.",
    )

    # WebSocket
    websocket_manager.send.assert_awaited_once()

    user_id, payload = (
        websocket_manager.send.await_args.args
    )

    assert user_id == "user-42"
    assert payload["id"] == result.id
    assert payload["type"] == notif_type.value
    assert payload["status"] == (
        NotificationStatus.UNREAD.value
    )
    assert payload["entity_type"] == entity_type.value
    assert payload["entity_id"] == "quote-42"


# ============================================================
# SEND UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_send_update_sends_websocket_update(
    service_with_websocket,
    websocket_manager,
):
    payload = {
        "type": "QUOTE_UPDATED",
        "count": 3,
    }

    await service_with_websocket.send_update(
        user_id="user-1",
        payload=payload,
    )

    websocket_manager.send.assert_awaited_once_with(
        "user-1",
        payload,
    )


# ============================================================
# SEND UPDATE — NO WEBSOCKET
# ============================================================


@pytest.mark.asyncio
async def test_send_update_does_nothing_without_websocket(
    service,
):
    payload = {
        "type": "QUOTE_UPDATED",
        "count": 3,
    }

    result = await service.send_update(
        user_id="user-1",
        payload=payload,
    )

    assert result is None


# ============================================================
# SEND UPDATE — WEBSOCKET ERROR
# ============================================================


@pytest.mark.asyncio
async def test_send_update_propagates_websocket_error(
    service_with_websocket,
    websocket_manager,
):
    websocket_manager.send.side_effect = RuntimeError(
        "websocket error"
    )

    payload = {
        "type": "QUOTE_UPDATED",
        "count": 3,
    }

    with pytest.raises(
        RuntimeError,
        match="websocket error",
    ):
        await service_with_websocket.send_update(
            user_id="user-1",
            payload=payload,
        )


# ============================================================
# EMAIL ERROR
# ============================================================


@pytest.mark.asyncio
async def test_send_propagates_email_error(
    service,
    notification_repo,
    email_service,
):
    notif_type = get_notification_type()

    email_service.send.side_effect = RuntimeError(
        "email error"
    )

    with pytest.raises(
        RuntimeError,
        match="email error",
    ):
        await service.send(
            user_id="user-1",
            title="Title",
            message="Message",
            notif_type=notif_type,
            email="customer@example.com",
        )

    # La notification est sauvegardée avant l'envoi de l'e-mail.
    notification_repo.save.assert_called_once()


# ============================================================
# REPOSITORY ERROR
# ============================================================


@pytest.mark.asyncio
async def test_send_propagates_repository_error(
    service,
    notification_repo,
    email_service,
):
    notif_type = get_notification_type()

    notification_repo.save.side_effect = RuntimeError(
        "repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        await service.send(
            user_id="user-1",
            title="Title",
            message="Message",
            notif_type=notif_type,
        )

    email_service.send.assert_not_called()