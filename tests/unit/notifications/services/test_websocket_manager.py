from unittest.mock import AsyncMock

import pytest

from modules.notifications.application.services.websocket_manager import (
    ConnectionManager,
)


@pytest.fixture
def manager():
    return ConnectionManager()


@pytest.fixture
def websocket():
    ws = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_connect_accepts_and_registers_websocket(manager, websocket):
    await manager.connect("user-1", websocket)

    websocket.accept.assert_awaited_once()
    assert manager.active_connections["user-1"] == [websocket]


@pytest.mark.asyncio
async def test_connect_allows_multiple_websockets_for_same_user(
    manager,
):
    ws1 = AsyncMock()
    ws2 = AsyncMock()

    await manager.connect("user-1", ws1)
    await manager.connect("user-1", ws2)

    assert manager.active_connections["user-1"] == [ws1, ws2]


def test_disconnect_removes_websocket(manager, websocket):
    manager.active_connections["user-1"].append(websocket)

    manager.disconnect("user-1", websocket)

    assert "user-1" not in manager.active_connections


def test_disconnect_keeps_other_websockets(manager):
    ws1 = AsyncMock()
    ws2 = AsyncMock()

    manager.active_connections["user-1"] = [ws1, ws2]

    manager.disconnect("user-1", ws1)

    assert manager.active_connections["user-1"] == [ws2]


def test_disconnect_unknown_user_does_nothing(manager, websocket):
    manager.disconnect("unknown-user", websocket)

    assert manager.active_connections == {}


def test_disconnect_unknown_websocket_does_nothing(manager):
    ws1 = AsyncMock()
    ws2 = AsyncMock()

    manager.active_connections["user-1"] = [ws1]

    manager.disconnect("user-1", ws2)

    assert manager.active_connections["user-1"] == [ws1]


@pytest.mark.asyncio
async def test_send_sends_message_to_all_user_websockets(manager):
    ws1 = AsyncMock()
    ws2 = AsyncMock()

    manager.active_connections["user-1"] = [ws1, ws2]

    message = {
        "id": "notification-1",
        "message": "Nouvelle notification",
    }

    await manager.send("user-1", message)

    ws1.send_json.assert_awaited_once_with(message)
    ws2.send_json.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_send_does_nothing_when_user_has_no_websocket(
    manager,
):
    await manager.send(
        "user-1",
        {"message": "test"},
    )

    assert manager.active_connections == {}


@pytest.mark.asyncio
async def test_broadcast_sends_message_to_all_connected_users(
    manager,
):
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    ws3 = AsyncMock()

    manager.active_connections["user-1"] = [ws1, ws2]
    manager.active_connections["user-2"] = [ws3]

    message = {
        "type": "NEW_NOTIFICATION",
        "message": "Test",
    }

    await manager.broadcast(message)

    ws1.send_json.assert_awaited_once_with(message)
    ws2.send_json.assert_awaited_once_with(message)
    ws3.send_json.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_broadcast_does_nothing_when_no_connections(manager):
    await manager.broadcast({"message": "test"})

    assert manager.active_connections == {}