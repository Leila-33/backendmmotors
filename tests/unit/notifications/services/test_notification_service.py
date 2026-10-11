import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.notifications.domain.enums import (
    NotificationStatus,
    NotificationType,
    NotificationEntityType,
)
from modules.notifications.domain.exceptions import (
    InvalidNotificationType,
    InvalidNotificationEntityType,
)
from modules.notifications.application.services.notification_service import (
    NotificationService,
)


@pytest.fixture
def notification_repo():
    return MagicMock()


@pytest.fixture
def email_service():
    return MagicMock()


@pytest.fixture
def redis_conn():
    redis = MagicMock()
    redis.publish.return_value = 1
    return redis


@pytest.fixture
def service(notification_repo, email_service, redis_conn):
    return NotificationService(
        notification_repo=notification_repo,
        email_service=email_service,
        redis_conn=redis_conn,
    )


@pytest.fixture
def valid_type():
    return next(iter(NotificationType))


@pytest.fixture
def valid_entity_type():
    return next(iter(NotificationEntityType))


@pytest.fixture
def notification_data(valid_type, valid_entity_type):
    return {
        "user_id": "user-123",
        "title": "Nouvelle notification",
        "message": "Votre dossier a été mis à jour.",
        "notif_type": valid_type,
        "email": None,
        "entity_type": valid_entity_type,
        "entity_id": "entity-123",
    }


# =========================================================
# SEND : CRÉATION ET PERSISTANCE
# =========================================================

@pytest.mark.asyncio
async def test_send_creates_and_persists_notification(
    service,
    notification_repo,
    notification_data,
):
    result = await service.send(**notification_data)

    assert result.user_id == "user-123"
    assert result.title == "Nouvelle notification"
    assert result.message == "Votre dossier a été mis à jour."
    assert result.type == notification_data["notif_type"]
    assert result.status == NotificationStatus.UNREAD
    assert result.entity_type == notification_data["entity_type"]
    assert result.entity_id == "entity-123"

    assert result.id
    assert isinstance(result.created_at, datetime)
    assert result.created_at.tzinfo is not None
    assert result.created_at.utcoffset().total_seconds() == 0

    notification_repo.save.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_send_generates_unique_notification_ids(
    service,
    notification_data,
):
    first = await service.send(**notification_data)
    second = await service.send(**notification_data)

    assert first.id != second.id


@pytest.mark.asyncio
async def test_send_allows_optional_entity_fields_to_be_none(
    service,
    notification_repo,
):
    result = await service.send(
        user_id="user-123",
        title="Information",
        message="Aucune entité associée.",
        notif_type=next(iter(NotificationType)),
    )

    assert result.entity_type is None
    assert result.entity_id is None
    notification_repo.save.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_send_converts_string_notification_type(
    service,
    notification_data,
):
    notification_data["notif_type"] = notification_data["notif_type"].value

    result = await service.send(**notification_data)

    assert result.type == NotificationType(
        notification_data["notif_type"]
    )


@pytest.mark.asyncio
async def test_send_converts_string_entity_type(
    service,
    notification_data,
):
    notification_data["entity_type"] = (
        notification_data["entity_type"].value
    )

    result = await service.send(**notification_data)

    assert result.entity_type == NotificationEntityType(
        notification_data["entity_type"]
    )


@pytest.mark.asyncio
async def test_send_rejects_invalid_notification_type(
    service,
    notification_repo,
):
    with pytest.raises(InvalidNotificationType):
        await service.send(
            user_id="user-123",
            title="Notification",
            message="Message",
            notif_type="INVALID_NOTIFICATION_TYPE",
        )

    notification_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_send_rejects_invalid_entity_type(
    service,
    notification_repo,
    valid_type,
):
    with pytest.raises(InvalidNotificationEntityType):
        await service.send(
            user_id="user-123",
            title="Notification",
            message="Message",
            notif_type=valid_type,
            entity_type="INVALID_ENTITY_TYPE",
        )

    notification_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_send_does_not_save_if_repository_fails(
    service,
    notification_repo,
    notification_data,
):
    notification_repo.save.side_effect = RuntimeError(
        "Erreur de persistance"
    )

    with pytest.raises(RuntimeError, match="Erreur de persistance"):
        await service.send(**notification_data)


# =========================================================
# ENVOI D'EMAIL
# =========================================================

@pytest.mark.asyncio
async def test_send_email_when_email_is_provided(
    service,
    email_service,
    notification_data,
):
    notification_data["email"] = "client@example.com"

    await service.send(**notification_data)

    email_service.send.assert_called_once_with(
        to="client@example.com",
        subject="Nouvelle notification",
        body="Votre dossier a été mis à jour.",
    )


@pytest.mark.asyncio
async def test_send_does_not_send_email_when_email_is_none(
    service,
    email_service,
    notification_data,
):
    notification_data["email"] = None

    await service.send(**notification_data)

    email_service.send.assert_not_called()


@pytest.mark.asyncio
async def test_send_does_not_send_email_when_email_is_empty(
    service,
    email_service,
    notification_data,
):
    notification_data["email"] = ""

    await service.send(**notification_data)

    email_service.send.assert_not_called()


@pytest.mark.asyncio
async def test_send_propagates_email_error(
    service,
    email_service,
    redis_conn,
    notification_data,
):
    notification_data["email"] = "client@example.com"
    email_service.send.side_effect = RuntimeError("Erreur email")

    with pytest.raises(RuntimeError, match="Erreur email"):
        await service.send(**notification_data)

    redis_conn.publish.assert_not_called()


# =========================================================
# PUBLICATION REDIS DE LA NOTIFICATION
# =========================================================

@pytest.mark.asyncio
async def test_send_publishes_notification_to_redis(
    service,
    redis_conn,
    notification_data,
):
    result = await service.send(**notification_data)

    redis_conn.publish.assert_called_once()

    channel, raw_event = redis_conn.publish.call_args.args

    assert channel == "user_notifications"

    event = json.loads(raw_event)

    assert event["user_id"] == "user-123"
    assert event["message"]["id"] == result.id
    assert event["message"]["title"] == result.title
    assert event["message"]["message"] == result.message
    assert event["message"]["type"] == result.type.value
    assert event["message"]["status"] == result.status.value
    assert event["message"]["entity_type"] == result.entity_type.value
    assert event["message"]["entity_id"] == result.entity_id
    assert event["message"]["created_at"] == result.created_at.isoformat()


@pytest.mark.asyncio
async def test_send_publishes_null_entity_type_when_not_provided(
    service,
    redis_conn,
):
    await service.send(
        user_id="user-123",
        title="Information",
        message="Message sans entité.",
        notif_type=next(iter(NotificationType)),
    )

    event = json.loads(redis_conn.publish.call_args.args[1])

    assert event["message"]["entity_type"] is None
    assert event["message"]["entity_id"] is None


@pytest.mark.asyncio
async def test_send_propagates_redis_publication_error(
    service,
    redis_conn,
    notification_repo,
    notification_data,
):
    redis_conn.publish.side_effect = RuntimeError("Erreur Redis")

    with pytest.raises(RuntimeError, match="Erreur Redis"):
        await service.send(**notification_data)

    # La notification a été persistée avant la publication Redis.
    notification_repo.save.assert_called_once()


# =========================================================
# SEND UPDATE : REDIS NON CONFIGURÉ
# =========================================================

@pytest.mark.asyncio
async def test_send_update_does_nothing_when_redis_is_none():
    service = NotificationService(
        notification_repo=MagicMock(),
        email_service=MagicMock(),
        redis_conn=None,
    )

    # Ne doit pas lever d'exception.
    await service.send_update(
        user_id="user-123",
        payload={"type": "TEST_EVENT"},
    )


@pytest.mark.asyncio
async def test_send_update_logs_warning_when_redis_is_none():
    service = NotificationService(
        notification_repo=MagicMock(),
        email_service=MagicMock(),
        redis_conn=None,
    )

    with patch(
        "modules.notifications.application.services.notification_service.logger"
    ) as logger_mock:
        await service.send_update(
            user_id="user-123",
            payload={"type": "TEST_EVENT"},
        )

    logger_mock.warning.assert_called_once()


# =========================================================
# SEND UPDATE : REDIS SYNCHRONE
# =========================================================

@pytest.mark.asyncio
async def test_send_update_publishes_json_event(
    service,
    redis_conn,
):
    payload = {
        "type": "NEW_MESSAGE",
        "message": "Bonjour",
    }

    await service.send_update(
        user_id="user-123",
        payload=payload,
    )

    redis_conn.publish.assert_called_once()

    channel, raw_event = redis_conn.publish.call_args.args

    assert channel == "user_notifications"

    event = json.loads(raw_event)

    assert event == {
        "user_id": "user-123",
        "message": payload,
    }


@pytest.mark.asyncio
async def test_send_update_converts_user_id_to_string(
    service,
    redis_conn,
):
    await service.send_update(
        user_id=123,
        payload={"type": "TEST_EVENT"},
    )

    event = json.loads(redis_conn.publish.call_args.args[1])

    assert event["user_id"] == "123"


# =========================================================
# SEND UPDATE : REDIS ASYNCHRONE
# =========================================================

@pytest.mark.asyncio
async def test_send_update_awaits_async_redis_publish(
    service,
    redis_conn,
):
    redis_conn.publish = AsyncMock(return_value=1)

    await service.send_update(
        user_id="user-123",
        payload={"type": "TEST_EVENT"},
    )

    redis_conn.publish.assert_awaited_once()


# =========================================================
# SEND UPDATE : GESTION DES ERREURS
# =========================================================

@pytest.mark.asyncio
async def test_send_update_logs_and_reraises_redis_error(
    service,
    redis_conn,
):
    redis_conn.publish.side_effect = RuntimeError("Redis indisponible")

    with patch(
        "modules.notifications.application.services.notification_service.logger"
    ) as logger_mock:
        with pytest.raises(
            RuntimeError,
            match="Redis indisponible",
        ):
            await service.send_update(
                user_id="user-123",
                payload={"type": "TEST_EVENT"},
            )

    logger_mock.exception.assert_called_once()


@pytest.mark.asyncio
async def test_send_update_handles_async_redis_publish_error(
    service,
    redis_conn,
):
    redis_conn.publish = AsyncMock(
        side_effect=RuntimeError("Erreur Redis asynchrone")
    )

    with pytest.raises(
        RuntimeError,
        match="Erreur Redis asynchrone",
    ):
        await service.send_update(
            user_id="user-123",
            payload={"type": "TEST_EVENT"},
        )