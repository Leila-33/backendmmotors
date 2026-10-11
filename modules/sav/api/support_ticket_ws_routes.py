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
)
from modules.dependencies.dependencies import (
    get_user_repository,
)
from modules.vehicles.infrastructure.queue.redis_connection import redis_conn
from modules.notifications.api.dependencies import (
    get_notification_service,
)
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["ws Support Tickets"]
)



logger = logging.getLogger(__name__)


@router.websocket("/{ticket_id}")
async def ticket_chat(
    websocket: WebSocket,
    ticket_id: str,
    chat_usecase=Depends(get_ticket_chat_usecase),
    notification_service=Depends(get_notification_service),
    jwt_service=Depends(get_jwt_service),
    user_repository=Depends(get_user_repository),
):
    # =====================================================
    # AUTHENTIFICATION
    # =====================================================

    token = websocket.query_params.get("token")

    logger.info(
        "WebSocket support-ticket : token présent=%s",
        bool(token),
    )

    if not token:
        await websocket.close(code=1008)
        return

    try:
        user = get_user_from_ws_token(
            websocket,
            jwt_service=jwt_service,
            user_repo=user_repository,
        )

        if not user:
            await websocket.close(code=1008)
            return

    except Exception:
        logger.exception("Erreur authentification WebSocket")
        await websocket.close(code=1008)
        return

    # =====================================================
    # VÉRIFICATION DES DROITS
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
        await websocket.close(code=1008)
        return

    # =====================================================
    # CONNEXION
    # =====================================================

    await chat_usecase.chat_manager.connect(
        ticket_id,
        websocket,
    )

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            # =============================================
            # MARQUER LE TICKET COMME LU
            # =============================================

            if data.get("type") == "MARK_AS_READ":
                try:
                    unread_count = chat_usecase.mark_as_read(
                        ticket_id=ticket_id,
                        user_id=user.id,
                        user_role=user.role,
                    )

                    await notification_service.send_update(
                        user_id=user.id,
                        payload={
                            "type": "UNREAD_TICKETS_UPDATED",
                            "count": unread_count,
                        },
                    )

                except Exception:
                    logger.exception(
                        "Impossible de marquer le ticket comme lu ou "
                        "de mettre à jour le compteur : ticket_id=%s, user_id=%s",
                        ticket_id,
                        user.id,
                    )

                    continue

            # =============================================
            # IGNORER LES ÉVÉNEMENTS NON PRIS EN CHARGE
            # =============================================

            if event_type != "NEW_MESSAGE":
                continue

            # =============================================
            # VALIDATION DU MESSAGE
            # =============================================

            try:
                payload = TicketMessageCreate(
                    **data["data"]
                )
            except (KeyError, TypeError, ValueError):
                await websocket.send_json({
                    "type": "ERROR",
                    "message": "Format du message invalide.",
                })
                continue

            # =============================================
            # CRÉATION DU MESSAGE
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
            # SÉRIALISATION
            # =============================================

            message_data = {
                "id": str(message.id),
                "ticket_id": str(message.ticket_id),
                "sender_id": str(message.sender_id),
                "sender_role": (
                    message.sender_role.value
                    if hasattr(message.sender_role, "value")
                    else message.sender_role
                ),
                "message": message.message,
                "created_at": (
                    message.created_at.isoformat()
                    if message.created_at
                    else datetime.now(timezone.utc).isoformat()
                ),
            }

            # =============================================
            # DIFFUSION DU MESSAGE À TOUTES LES INSTANCES
            # =============================================

            redis_payload = {
                "ticket_id": str(ticket_id),
                "payload": {
                    "type": "NEW_MESSAGE",
                    "data": message_data,
                },
            }

            redis_conn.publish(
                "ticket_chat_updates",
                json.dumps(redis_payload),
            )

            # =============================================
            # NOTIFICATION DU DESTINATAIRE
            # =============================================

            recipient = chat_usecase.get_recipient(
                ticket=ticket,
                sender_id=user.id,
            )

            if not recipient:
                logger.warning(
                    "Aucun destinataire trouvé pour ticket_id=%s",
                    ticket_id,
                )
                continue

            recipient_id, recipient_role = recipient

            unread_count = chat_usecase.ticket_repository.count_unread(
                user_id=recipient_id,
                user_role=recipient_role,
            )

            try:
                await notification_service.send_update(
                    user_id=str(recipient_id),
                    payload={
                        "type": "UNREAD_TICKETS_UPDATED",
                        "count": unread_count,
                    },
                )

            except Exception:
                logger.exception(
                    "Échec de mise à jour du compteur non lu : user_id=%s",
                    recipient_id,
                )

    except WebSocketDisconnect:
        logger.info(
            "WebSocket fermé : ticket_id=%s, user_id=%s",
            ticket_id,
            user.id,
        )

    except Exception:
        logger.exception(
            "Erreur WebSocket : ticket_id=%s, user_id=%s",
            ticket_id,
            user.id,
        )

    finally:
        chat_usecase.chat_manager.disconnect(
            ticket_id,
            websocket,
        )