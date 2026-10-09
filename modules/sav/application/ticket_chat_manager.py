from collections import defaultdict
from fastapi import WebSocket


import logging
from collections import defaultdict

from fastapi import WebSocket


logger = logging.getLogger(__name__)


class TicketChatManager:
    """
    Gère les connexions WebSocket associées aux tickets SAV.

    Chaque instance FastAPI conserve uniquement ses connexions locales.
    La diffusion entre les instances est assurée par Redis Pub/Sub.
    """

    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(
        self,
        ticket_id: str,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()

        ticket_id = str(ticket_id)
        self.rooms[ticket_id].append(websocket)

        logger.info(
            "WebSocket chat connecté : ticket_id=%s, connexions=%s",
            ticket_id,
            len(self.rooms[ticket_id]),
        )

    def disconnect(
        self,
        ticket_id: str,
        websocket: WebSocket,
    ) -> None:
        ticket_id = str(ticket_id)
        sockets = self.rooms.get(ticket_id)

        if not sockets:
            return

        if websocket in sockets:
            sockets.remove(websocket)

        if not sockets:
            self.rooms.pop(ticket_id, None)

        logger.info(
            "WebSocket chat déconnecté : ticket_id=%s",
            ticket_id,
        )

    async def broadcast_local(
        self,
        ticket_id: str,
        payload: dict,
    ) -> None:
        """
        Diffuse un événement aux connexions locales du ticket.
        Cette méthode est appelée par le listener Redis sur chaque instance.
        """
        ticket_id = str(ticket_id)
        sockets = list(self.rooms.get(ticket_id, []))

        if not sockets:
            logger.debug(
                "Aucun WebSocket local pour le ticket %s",
                ticket_id,
            )
            return

        disconnected = []

        for websocket in sockets:
            try:
                await websocket.send_json(payload)
            except Exception:
                logger.exception(
                    "Échec d'envoi WebSocket : ticket_id=%s",
                    ticket_id,
                )
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(ticket_id, websocket)

    async def broadcast(
        self,
        ticket_id: str,
        payload: dict,
    ) -> None:
        """
        Diffusion locale uniquement.

        Pour une diffusion entre api1 et api2, publier l'événement dans
        Redis depuis la route, puis appeler broadcast_local() dans le
        listener Redis de chaque instance.
        """
        await self.broadcast_local(ticket_id, payload)


ticket_chat_manager = TicketChatManager()