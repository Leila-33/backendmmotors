from collections import defaultdict

from fastapi import WebSocket


from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """
    Gère les connexions WebSocket actives des utilisateurs
    et permet d'envoyer des messages à leurs différentes connexions.
    """

    def __init__(self):
        # user_id -> list of sockets
        self.active_connections: dict[
            str,
            list[WebSocket],
        ] = defaultdict(list)

    # =====================
    # CONNECT
    # =====================

    async def connect(
        self,
        user_id: str,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()

        self.active_connections[user_id].append(
            websocket
        )

        print("WS CONNECTED:", user_id)
        print(
            "ACTIVE CONNECTIONS:",
            self.active_connections,
        )

    # =====================
    # DISCONNECT
    # =====================

    def disconnect(
        self,
        user_id: str,
        websocket: WebSocket,
    ) -> None:
        sockets = self.active_connections.get(user_id)

        if not sockets:
            return

        if websocket in sockets:
            sockets.remove(websocket)

        if not sockets:
            del self.active_connections[user_id]

    # =====================
    # SEND TO USER
    # =====================

    async def send(
        self,
        user_id: str,
        message: dict,
    ) -> None:
        """
        Envoie un message à toutes les connexions
        WebSocket d'un utilisateur.
        """

        sockets = self.active_connections.get(
            user_id,
            [],
        )

        if not sockets:
            return

        for websocket in sockets:
            await websocket.send_json(message)

    # =====================
    # BROADCAST TO ALL USERS
    # =====================

    async def broadcast(
        self,
        message: dict,
    ) -> None:
        """
        Envoie un message à tous les utilisateurs
        actuellement connectés.
        """

        for sockets in self.active_connections.values():
            for websocket in sockets:
                await websocket.send_json(message)


manager = ConnectionManager()