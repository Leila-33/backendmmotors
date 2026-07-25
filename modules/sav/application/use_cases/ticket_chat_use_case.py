from fastapi import WebSocket, WebSocketDisconnect

from websocket.auth import get_user_from_ws_token
from modules.auth.domain.enums import UserRole
from modules.sav.api.schemas import TicketMessageCreate
from fastapi import WebSocket, WebSocketDisconnect


class TicketChatUseCase:

    def __init__(
        self,
        manager,
        connection_manager,
        jwt_service,
        user_repo,
        blacklist_repo,
        ticket_repo,
        read_state_repo,
        create_message_uc,
    ):
        self.manager = manager
        self.connection_manager = connection_manager

        self.jwt_service = jwt_service
        self.user_repo = user_repo
        self.blacklist_repo = blacklist_repo

        self.ticket_repo = ticket_repo
        self.read_state_repo = read_state_repo

        self.create_message_uc = create_message_uc

    async def handle_connection(
        self,
        websocket: WebSocket,
        ticket_id: str,
    ):

        token = websocket.query_params.get("token")

        # =====================
        # AUTH
        # =====================
        if not token:
            await websocket.close(code=1008)
            return

        user = get_user_from_ws_token(
            websocket,
            jwt_service=self.jwt_service,
            user_repo=self.user_repo,
            blacklist_repo=self.blacklist_repo,
        )

        if not user:
            await websocket.close(code=1008)
            return

        # =====================
        # LOAD TICKET
        # =====================
        ticket = self.ticket_repo.get_by_id(ticket_id)

        if not ticket:
            await websocket.close(code=1008)
            return

        # =====================
        # ACCESS
        # =====================
        if (
            user.role == UserRole.CLIENT
            and ticket.user_id != user.id
        ):
            await websocket.close(code=1008)
            return

        # =====================
        # CONNECT
        # =====================
        await self.manager.connect(ticket_id, websocket)

        try:

            while True:

                data = await websocket.receive_json()

                if data.get("type") != "NEW_MESSAGE":
                    continue

                payload = TicketMessageCreate(**data["data"])

                message = self.create_message_uc.execute(
                    ticket_id=ticket_id,
                    user=user,
                    payload=payload,
                )

                # =====================
                # CHAT ROOM
                # =====================
                await self.manager.broadcast(
                    ticket_id,
                    {
                        "type": "NEW_MESSAGE",
                        "data": {
                            "id": message.id,
                            "ticket_id": message.ticket_id,
                            "sender_id": message.sender_id,
                            "sender_role": message.sender_role,
                            "message": message.message,
                            "created_at": message.created_at.isoformat(),
                        },
                    },
                )

                # =====================
                # DESTINATAIRE
                # =====================
                recipient_id = (
                    ticket.assigned_to
                    if user.id == ticket.user_id
                    else ticket.user_id
                )

                if recipient_id:

                    unread = self.read_state_repo.count_unread(
                        recipient_id
                    )

                    await self.connection_manager.send(
                        recipient_id,
                        {
                            "type": "UNREAD_TICKETS_UPDATED",
                            "count": unread,
                        },
                    )

        except WebSocketDisconnect:

            self.manager.disconnect(
                ticket_id,
                websocket,
            )