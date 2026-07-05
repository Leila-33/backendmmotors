from collections import defaultdict
from fastapi import WebSocket


class TicketChatManager:

    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(
        self,
        ticket_id: str,
        websocket: WebSocket
    ):
        await websocket.accept()
        self.rooms[ticket_id].append(websocket)

    def disconnect(
        self,
        ticket_id: str,
        websocket: WebSocket
    ):
        if websocket in self.rooms[ticket_id]:
            self.rooms[ticket_id].remove(websocket)

        if not self.rooms[ticket_id]:
            del self.rooms[ticket_id]

    async def broadcast(
        self,
        ticket_id: str,
        payload: dict
    ):
        for ws in list(self.rooms.get(ticket_id, [])):
            await ws.send_json(payload)

ticket_chat_manager = TicketChatManager()