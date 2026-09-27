from collections import defaultdict
from fastapi import WebSocket


class ConnectionManager:
    """
    Gère les connexions WebSocket actives des utilisateurs
    et permet d'envoyer des messages à leurs différentes connexions.
    """
    def __init__(self):
        # user_id -> list of sockets
        self.active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    # =====================
    # CONNECT
    # =====================
    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id].append(websocket)
        print(" WS CONNECTED:", user_id)
        print(" ACTIVE CONNECTIONS 1:", self.active_connections)

    # =====================
    # DISCONNECT
    # =====================
    def disconnect(self, user_id: str, websocket: WebSocket):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    # =====================
    # SEND TO USER (ALL DEVICES)
    # =====================
    async def send(self, user_id: str, message: dict):
        sockets = self.active_connections.get(user_id, [])
        print(" SEND TO USER:", user_id)
        print(" ACTIVE CONNECTIONS 2:", self.active_connections)

        if not sockets:
            print("NO WS FOUND")
            return

        for ws in sockets:
            await ws.send_json(message)

        print("MESSAGE SENT")

    # =====================
    # BROADCAST TO ALL USERS
    # =====================
    async def broadcast(self, message: dict):
        for sockets in self.active_connections.values():
            for ws in sockets:
                await ws.send_json(message)

manager = ConnectionManager()