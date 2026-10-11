from collections import defaultdict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from modules.sav.application.ticket_chat_manager import (
    TicketChatManager,
)


@pytest.fixture
def manager():
    return TicketChatManager()


@pytest.fixture
def websocket():
    ws = MagicMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


# =========================================================
# INITIALISATION
# =========================================================

def test_manager_initializes_empty_rooms(manager):
    assert isinstance(manager.rooms, defaultdict)
    assert manager.rooms.default_factory is list
    assert len(manager.rooms) == 0


# =========================================================
# CONNECT
# =========================================================

@pytest.mark.asyncio
async def test_connect_accepts_websocket_and_registers_connection(
    manager,
    websocket,
):
    await manager.connect("ticket-123", websocket)

    websocket.accept.assert_awaited_once_with()
    assert manager.rooms["ticket-123"] == [websocket]


@pytest.mark.asyncio
async def test_connect_converts_ticket_id_to_string(
    manager,
    websocket,
):
    await manager.connect(123, websocket)

    assert "123" in manager.rooms
    assert manager.rooms["123"] == [websocket]


@pytest.mark.asyncio
async def test_connect_allows_multiple_connections_for_same_ticket(
    manager,
):
    websocket_1 = MagicMock()
    websocket_1.accept = AsyncMock()

    websocket_2 = MagicMock()
    websocket_2.accept = AsyncMock()

    await manager.connect("ticket-123", websocket_1)
    await manager.connect("ticket-123", websocket_2)

    assert manager.rooms["ticket-123"] == [
        websocket_1,
        websocket_2,
    ]


@pytest.mark.asyncio
async def test_connect_does_not_register_websocket_if_accept_fails(
    manager,
    websocket,
):
    websocket.accept.side_effect = RuntimeError("Connexion refusée")

    with pytest.raises(RuntimeError, match="Connexion refusée"):
        await manager.connect("ticket-123", websocket)

    assert "ticket-123" not in manager.rooms


@pytest.mark.asyncio
async def test_connect_logs_connection(
    manager,
    websocket,
):
    with patch(
        "modules.sav.application.ticket_chat_manager.logger"
    ) as logger_mock:
        await manager.connect("ticket-123", websocket)

    logger_mock.info.assert_called_once()


# =========================================================
# DISCONNECT
# =========================================================

def test_disconnect_removes_websocket_from_room(
    manager,
    websocket,
):
    manager.rooms["ticket-123"] = [websocket]

    manager.disconnect("ticket-123", websocket)

    assert "ticket-123" not in manager.rooms


def test_disconnect_keeps_other_connections(
    manager,
):
    websocket_1 = MagicMock()
    websocket_2 = MagicMock()

    manager.rooms["ticket-123"] = [
        websocket_1,
        websocket_2,
    ]

    manager.disconnect("ticket-123", websocket_1)

    assert manager.rooms["ticket-123"] == [websocket_2]


def test_disconnect_removes_empty_room(
    manager,
):
    websocket = MagicMock()
    manager.rooms["ticket-123"] = [websocket]

    manager.disconnect("ticket-123", websocket)

    assert "ticket-123" not in manager.rooms


def test_disconnect_does_nothing_if_room_does_not_exist(
    manager,
    websocket,
):
    manager.disconnect("ticket-unknown", websocket)

    assert len(manager.rooms) == 0


def test_disconnect_does_nothing_if_websocket_is_not_registered(
    manager,
    websocket,
):
    other_websocket = MagicMock()
    manager.rooms["ticket-123"] = [other_websocket]

    manager.disconnect("ticket-123", websocket)

    assert manager.rooms["ticket-123"] == [other_websocket]


def test_disconnect_converts_ticket_id_to_string(
    manager,
    websocket,
):
    manager.rooms["123"] = [websocket]

    manager.disconnect(123, websocket)

    assert "123" not in manager.rooms


def test_disconnect_logs_when_room_exists(
    manager,
    websocket,
):
    manager.rooms["ticket-123"] = [websocket]

    with patch(
        "modules.sav.application.ticket_chat_manager.logger"
    ) as logger_mock:
        manager.disconnect("ticket-123", websocket)

    logger_mock.info.assert_called_once()


# =========================================================
# BROADCAST LOCAL
# =========================================================

@pytest.mark.asyncio
async def test_broadcast_local_sends_payload_to_all_connections(
    manager,
):
    websocket_1 = MagicMock()
    websocket_1.send_json = AsyncMock()

    websocket_2 = MagicMock()
    websocket_2.send_json = AsyncMock()

    manager.rooms["ticket-123"] = [
        websocket_1,
        websocket_2,
    ]

    payload = {
        "type": "NEW_MESSAGE",
        "message": "Bonjour",
    }

    await manager.broadcast_local("ticket-123", payload)

    websocket_1.send_json.assert_awaited_once_with(payload)
    websocket_2.send_json.assert_awaited_once_with(payload)


@pytest.mark.asyncio
async def test_broadcast_local_does_nothing_without_connections(
    manager,
):
    await manager.broadcast_local(
        "ticket-unknown",
        {"type": "NEW_MESSAGE"},
    )

    assert len(manager.rooms) == 0


@pytest.mark.asyncio
async def test_broadcast_local_converts_ticket_id_to_string(
    manager,
):
    websocket = MagicMock()
    websocket.send_json = AsyncMock()
    manager.rooms["123"] = [websocket]

    payload = {"type": "NEW_MESSAGE"}

    await manager.broadcast_local(123, payload)

    websocket.send_json.assert_awaited_once_with(payload)


@pytest.mark.asyncio
async def test_broadcast_local_removes_websocket_when_send_fails(
    manager,
):
    websocket = MagicMock()
    websocket.send_json = AsyncMock(
        side_effect=RuntimeError("Connexion fermée")
    )
    manager.rooms["ticket-123"] = [websocket]

    await manager.broadcast_local(
        "ticket-123",
        {"type": "NEW_MESSAGE"},
    )

    assert "ticket-123" not in manager.rooms


@pytest.mark.asyncio
async def test_broadcast_local_keeps_healthy_connections(
    manager,
):
    failing_websocket = MagicMock()
    failing_websocket.send_json = AsyncMock(
        side_effect=RuntimeError("Connexion fermée")
    )

    healthy_websocket = MagicMock()
    healthy_websocket.send_json = AsyncMock()

    manager.rooms["ticket-123"] = [
        failing_websocket,
        healthy_websocket,
    ]

    payload = {"type": "NEW_MESSAGE"}

    await manager.broadcast_local("ticket-123", payload)

    healthy_websocket.send_json.assert_awaited_once_with(payload)
    assert manager.rooms["ticket-123"] == [healthy_websocket]


@pytest.mark.asyncio
async def test_broadcast_local_continues_after_one_send_fails(
    manager,
):
    failing_websocket = MagicMock()
    failing_websocket.send_json = AsyncMock(
        side_effect=Exception("Erreur d'envoi")
    )

    healthy_websocket = MagicMock()
    healthy_websocket.send_json = AsyncMock()

    manager.rooms["ticket-123"] = [
        failing_websocket,
        healthy_websocket,
    ]

    payload = {"type": "NEW_MESSAGE"}

    await manager.broadcast_local("ticket-123", payload)

    healthy_websocket.send_json.assert_awaited_once_with(payload)


@pytest.mark.asyncio
async def test_broadcast_local_logs_send_failure(
    manager,
):
    websocket = MagicMock()
    websocket.send_json = AsyncMock(
        side_effect=RuntimeError("Connexion fermée")
    )
    manager.rooms["ticket-123"] = [websocket]

    with patch(
        "modules.sav.application.ticket_chat_manager.logger"
    ) as logger_mock:
        await manager.broadcast_local(
            "ticket-123",
            {"type": "NEW_MESSAGE"},
        )

    logger_mock.exception.assert_called_once()


@pytest.mark.asyncio
async def test_broadcast_local_does_not_modify_room_during_iteration(
    manager,
):
    websocket_1 = MagicMock()
    websocket_1.send_json = AsyncMock(
        side_effect=RuntimeError("Connexion fermée")
    )

    websocket_2 = MagicMock()
    websocket_2.send_json = AsyncMock()

    websocket_3 = MagicMock()
    websocket_3.send_json = AsyncMock()

    manager.rooms["ticket-123"] = [
        websocket_1,
        websocket_2,
        websocket_3,
    ]

    await manager.broadcast_local(
        "ticket-123",
        {"type": "NEW_MESSAGE"},
    )

    websocket_2.send_json.assert_awaited_once()
    websocket_3.send_json.assert_awaited_once()
    assert manager.rooms["ticket-123"] == [
        websocket_2,
        websocket_3,
    ]


# =========================================================
# BROADCAST
# =========================================================

@pytest.mark.asyncio
async def test_broadcast_delegates_to_broadcast_local(
    manager,
):
    payload = {"type": "NEW_MESSAGE"}

    with patch.object(
        manager,
        "broadcast_local",
        new_callable=AsyncMock,
    ) as broadcast_local_mock:
        await manager.broadcast("ticket-123", payload)

    broadcast_local_mock.assert_awaited_once_with(
        "ticket-123",
        payload,
    )


@pytest.mark.asyncio
async def test_broadcast_sends_payload_to_connected_clients(
    manager,
):
    websocket = MagicMock()
    websocket.send_json = AsyncMock()
    manager.rooms["ticket-123"] = [websocket]

    payload = {
        "type": "NEW_MESSAGE",
        "message": "Bonjour",
    }

    await manager.broadcast("ticket-123", payload)

    websocket.send_json.assert_awaited_once_with(payload)


@pytest.mark.asyncio
async def test_broadcast_propagates_unexpected_broadcast_local_error(
    manager,
):
    with patch.object(
        manager,
        "broadcast_local",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Erreur de diffusion"),
    ):
        with pytest.raises(
            RuntimeError,
            match="Erreur de diffusion",
        ):
            await manager.broadcast(
                "ticket-123",
                {"type": "NEW_MESSAGE"},
            )


# =========================================================
# INSTANCE GLOBALE
# =========================================================

def test_global_ticket_chat_manager_is_initialized():
    from modules.sav.application.ticket_chat_manager import (
        ticket_chat_manager,
    )

    assert isinstance(ticket_chat_manager, TicketChatManager)