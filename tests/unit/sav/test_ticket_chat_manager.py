from unittest.mock import AsyncMock, Mock

import pytest

from modules.sav.application.ticket_chat_manager import TicketChatManager


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def manager():
    return TicketChatManager()


@pytest.fixture
def websocket():
    ws = Mock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


# ============================================================
# CONNECT
# ============================================================


@pytest.mark.asyncio
async def test_connect_accepts_websocket(
    manager,
    websocket,
):
    await manager.connect(
        ticket_id="ticket-1",
        websocket=websocket,
    )

    websocket.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_adds_websocket_to_room(
    manager,
    websocket,
):
    await manager.connect(
        ticket_id="ticket-1",
        websocket=websocket,
    )

    assert websocket in manager.rooms["ticket-1"]


@pytest.mark.asyncio
async def test_connect_adds_multiple_websockets_to_same_room(
    manager,
):
    websocket_1 = Mock()
    websocket_1.accept = AsyncMock()

    websocket_2 = Mock()
    websocket_2.accept = AsyncMock()

    await manager.connect(
        ticket_id="ticket-1",
        websocket=websocket_1,
    )

    await manager.connect(
        ticket_id="ticket-1",
        websocket=websocket_2,
    )

    assert manager.rooms["ticket-1"] == [
        websocket_1,
        websocket_2,
    ]


@pytest.mark.asyncio
async def test_connect_keeps_websockets_in_separate_rooms(
    manager,
):
    websocket_1 = Mock()
    websocket_1.accept = AsyncMock()

    websocket_2 = Mock()
    websocket_2.accept = AsyncMock()

    await manager.connect(
        ticket_id="ticket-1",
        websocket=websocket_1,
    )

    await manager.connect(
        ticket_id="ticket-2",
        websocket=websocket_2,
    )

    assert manager.rooms["ticket-1"] == [websocket_1]
    assert manager.rooms["ticket-2"] == [websocket_2]


# ============================================================
# DISCONNECT
# ============================================================


def test_disconnect_removes_websocket_from_room(
    manager,
    websocket,
):
    manager.rooms["ticket-1"].append(websocket)

    manager.disconnect(
        ticket_id="ticket-1",
        websocket=websocket,
    )

    assert websocket not in manager.rooms["ticket-1"]


def test_disconnect_deletes_empty_room(
    manager,
    websocket,
):
    manager.rooms["ticket-1"].append(websocket)

    manager.disconnect(
        ticket_id="ticket-1",
        websocket=websocket,
    )

    assert "ticket-1" not in manager.rooms


def test_disconnect_keeps_room_when_other_clients_remain(
    manager,
):
    websocket_1 = Mock()
    websocket_2 = Mock()

    manager.rooms["ticket-1"].extend(
        [websocket_1, websocket_2]
    )

    manager.disconnect(
        ticket_id="ticket-1",
        websocket=websocket_1,
    )

    assert "ticket-1" in manager.rooms
    assert manager.rooms["ticket-1"] == [
        websocket_2
    ]


def test_disconnect_does_not_remove_other_websocket(
    manager,
):
    websocket_1 = Mock()
    websocket_2 = Mock()

    manager.rooms["ticket-1"].extend(
        [websocket_1, websocket_2]
    )

    manager.disconnect(
        ticket_id="ticket-1",
        websocket=websocket_1,
    )

    assert websocket_2 in manager.rooms["ticket-1"]


def test_disconnect_websocket_not_present(
    manager,
    websocket,
):
    manager.rooms["ticket-1"].append(
        Mock()
    )

    manager.disconnect(
        ticket_id="ticket-1",
        websocket=websocket,
    )

    assert manager.rooms["ticket-1"]


def test_disconnect_from_empty_room_deletes_room(
    manager,
    websocket,
):
    # defaultdict crée la room lors de l'accès
    manager.rooms["ticket-1"]

    manager.disconnect(
        ticket_id="ticket-1",
        websocket=websocket,
    )

    assert "ticket-1" not in manager.rooms


# ============================================================
# BROADCAST
# ============================================================


@pytest.mark.asyncio
async def test_broadcast_sends_payload_to_websocket(
    manager,
):
    websocket = Mock()
    websocket.send_json = AsyncMock()

    manager.rooms["ticket-1"].append(websocket)

    payload = {
        "type": "MESSAGE_CREATED",
        "message": "Bonjour",
    }

    await manager.broadcast(
        ticket_id="ticket-1",
        payload=payload,
    )

    websocket.send_json.assert_awaited_once_with(
        payload
    )


@pytest.mark.asyncio
async def test_broadcast_sends_payload_to_all_websockets(
    manager,
):
    websocket_1 = Mock()
    websocket_1.send_json = AsyncMock()

    websocket_2 = Mock()
    websocket_2.send_json = AsyncMock()

    websocket_3 = Mock()
    websocket_3.send_json = AsyncMock()

    manager.rooms["ticket-1"].extend(
        [
            websocket_1,
            websocket_2,
            websocket_3,
        ]
    )

    payload = {
        "type": "MESSAGE_CREATED",
        "message": "Bonjour",
    }

    await manager.broadcast(
        ticket_id="ticket-1",
        payload=payload,
    )

    websocket_1.send_json.assert_awaited_once_with(
        payload
    )

    websocket_2.send_json.assert_awaited_once_with(
        payload
    )

    websocket_3.send_json.assert_awaited_once_with(
        payload
    )


@pytest.mark.asyncio
async def test_broadcast_does_not_send_to_other_room(
    manager,
):
    websocket_1 = Mock()
    websocket_1.send_json = AsyncMock()

    websocket_2 = Mock()
    websocket_2.send_json = AsyncMock()

    manager.rooms["ticket-1"].append(websocket_1)
    manager.rooms["ticket-2"].append(websocket_2)

    payload = {
        "type": "MESSAGE_CREATED",
        "message": "Bonjour",
    }

    await manager.broadcast(
        ticket_id="ticket-1",
        payload=payload,
    )

    websocket_1.send_json.assert_awaited_once_with(
        payload
    )

    websocket_2.send_json.assert_not_awaited()


@pytest.mark.asyncio
async def test_broadcast_to_non_existing_room_does_nothing(
    manager,
):
    payload = {
        "type": "MESSAGE_CREATED",
        "message": "Bonjour",
    }

    await manager.broadcast(
        ticket_id="ticket-inexistant",
        payload=payload,
    )

    assert "ticket-inexistant" not in manager.rooms


@pytest.mark.asyncio
async def test_broadcast_uses_copy_of_websocket_list(
    manager,
):
    websocket_1 = Mock()
    websocket_1.send_json = AsyncMock()

    websocket_2 = Mock()
    websocket_2.send_json = AsyncMock()

    manager.rooms["ticket-1"].extend(
        [websocket_1, websocket_2]
    )

    payload = {
        "type": "MESSAGE_CREATED",
        "message": "Bonjour",
    }

    await manager.broadcast(
        ticket_id="ticket-1",
        payload=payload,
    )

    websocket_1.send_json.assert_awaited_once_with(
        payload
    )

    websocket_2.send_json.assert_awaited_once_with(
        payload
    )