from datetime import datetime, timezone
import json
import logging

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
)
from modules.sav.application.dtos.create_ticket_message_dto import CreateTicketMessageDTO
from modules.sav.api.schemas import TicketMessageCreate

from websocket.auth import get_user_from_ws_token

from modules.sav.api.dependencies import (
    get_ticket_chat_usecase,
)

from modules.auth.api.dependencies import (
    get_jwt_service,
    get_user_repository,
)
from modules.vehicles.infrastructure.queue.redis_connection import redis_conn

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["ws Support Tickets"]
)


@router.websocket(
    "/{ticket_id}"
)
async def ticket_chat(
    websocket: WebSocket,
    ticket_id: str,

    chat_usecase=Depends(
        get_ticket_chat_usecase
    ),

    jwt_service=Depends(
        get_jwt_service
    ),

    user_repository=Depends(
        get_user_repository
    ),
):

    # =====================================================
    # AUTHENTICATION
    # =====================================================

    token = websocket.query_params.get(
        "token"
    )
    logger.info(
        "WebSocket support-ticket : token présent=%s",
        bool(token),
    )

    if not token:
        await websocket.close(
            code=1008
        )
        return

    try:
        user = get_user_from_ws_token(
            websocket,
            jwt_service=jwt_service,
            user_repo=user_repository,
        )

        logger.info(
            "Utilisateur WebSocket : %s",
            user.id if user else None,
        )

    except Exception:
        logger.exception(
            "Erreur authentification WebSocket"
        )
        await websocket.close(code=1008)
        return


    if not user:
        logger.warning(
            "WebSocket refusé : utilisateur introuvable"
        )
        await websocket.close(code=1008)
        return

    # =====================================================
    # ACCESS
    # =====================================================

    try:

        ticket = chat_usecase.check_access(
            ticket_id=ticket_id,
            user_id=user.id,
            user_role=user.role,
        )

    except Exception:

        logger.exception(
            "Accès WebSocket refusé",
            extra={
                "ticket_id": ticket_id,
                "user_id": user.id,
            },
        )

        await websocket.close(
            code=1008
        )
        return

    # =====================================================
    # CONNECT
    # =====================================================

    await chat_usecase.chat_manager.connect(
        ticket_id,
        websocket,
    )

    try:

        while True:

            data = (
                await websocket.receive_json()
            )

            if data.get("type") != "NEW_MESSAGE":
                continue

            payload = TicketMessageCreate(
                **data["data"]
            )

            # =============================================
            # CREATE MESSAGE
            # =============================================

            dto = CreateTicketMessageDTO(
                ticket_id=ticket_id,
                message=payload.message,
            )

            ticket, message = chat_usecase.send_message(
                dto=dto,
                user_id=user.id,
                user_role=user.role,
            )

            # =============================================
            # SERIALIZE
            # =============================================

            message_data = {
                "id": message.id,

                "ticket_id": message.ticket_id,

                "sender_id": message.sender_id,

                "sender_role": (
                    message.sender_role.value
                    if hasattr(
                        message.sender_role,
                        "value"
                    )
                    else message.sender_role
                ),

                "message": message.message,

                "created_at": (
                    message.created_at.isoformat()
                    if message.created_at
                    else datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
            }

            # =============================================
            # BROADCAST
            # =============================================

            await chat_usecase.chat_manager.broadcast(
                ticket_id,
                {
                    "type": "NEW_MESSAGE",
                    "data": message_data,
                },
            )

            # =============================================
            # RECIPIENT
            # =============================================

            recipient = chat_usecase.get_recipient(
                ticket=ticket,
                sender_id=user.id,
            )


            if recipient:
                recipient_id, recipient_role = recipient

                logger.info(
                    "[SAV WS] Destinataire trouvé : id=%s, role=%s",
                    recipient_id,
                    recipient_role,
                )

                unread = chat_usecase.ticket_repository.count_unread(
                    user_id=recipient_id,
                    user_role=recipient_role,
                )

                payload = {
                    "user_id": str(recipient_id),
                    "message": {
                        "type": "UNREAD_TICKETS_UPDATED",
                        "count": unread,
                    },
                }

                try:
                    subscribers = redis_conn.publish(
                        "user_notifications",
                        json.dumps(payload),
                    )

                    logger.info(
                        "[SAV WS] Publication Redis terminée : "
                        "channel=user_notifications, subscribers=%s, payload=%s",
                        subscribers,
                        payload,
                    )

                except Exception:
                    logger.exception("[SAV WS] Échec publication Redis")

            else:
                logger.warning(
                    "[SAV WS] Aucun destinataire trouvé pour ticket_id=%s",
                    ticket_id,
                )


    except WebSocketDisconnect:

        chat_usecase.chat_manager.disconnect(
            ticket_id,
            websocket,
        )

    except Exception:

        chat_usecase.chat_manager.disconnect(
            ticket_id,
            websocket,
        )

        raise