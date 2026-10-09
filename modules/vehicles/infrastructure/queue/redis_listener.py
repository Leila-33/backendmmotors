import asyncio
import json
import logging
from modules.vehicles.infrastructure.queue.redis_connection import redis_conn
from modules.notifications.application.services.websocket_manager import manager
from modules.sav.application.ticket_chat_manager import ticket_chat_manager

logger = logging.getLogger(__name__)


def start_redis_listener(loop):
    pubsub = redis_conn.pubsub()

    pubsub.subscribe(
        "inspection_updates",
        "reconditioning_updates",
        "user_notifications",
        "ticket_chat_updates",
    )

    logger.info("Redis listener started")

    try:
        for message in pubsub.listen():
            if message["type"] != "message":
                continue

            try:
                channel = message["channel"]

                if isinstance(channel, bytes):
                    channel = channel.decode("utf-8")

                raw_data = message["data"]

                if isinstance(raw_data, bytes):
                    raw_data = raw_data.decode("utf-8")

                data = json.loads(raw_data)

                # =========================================
                # CHAT SAV
                # =========================================
                if channel == "ticket_chat_updates":
                    ticket_id = data.get("ticket_id")
                    payload = data.get("payload")

                    if not ticket_id or not isinstance(payload, dict):
                        logger.warning(
                            "Événement chat Redis invalide : %s",
                            data,
                        )
                        continue

                    future = asyncio.run_coroutine_threadsafe(
                        ticket_chat_manager.broadcast_local(
                            str(ticket_id),
                            payload,
                        ),
                        loop,
                    )

                    logger.debug(
                        "Événement chat Redis reçu : ticket_id=%s",
                        ticket_id,
                    )
                    continue

                # =========================================
                # NOTIFICATIONS UTILISATEUR
                # =========================================
                if channel == "user_notifications":
                    user_id = data.get("user_id")
                    payload = data.get("message")

                    if not user_id or not isinstance(payload, dict):
                        logger.warning(
                            "Notification Redis invalide : %s",
                            data,
                        )
                        continue

                    asyncio.run_coroutine_threadsafe(
                        manager.send(str(user_id), payload),
                        loop,
                    )
                    continue

                # =========================================
                # INSPECTIONS / RECONDITIONNEMENT
                # =========================================
                event = data.get("event")
                user_id = data.get("user_id")

                if not user_id:
                    logger.warning(
                        "Événement Redis sans user_id : %s",
                        data,
                    )
                    continue

                if event in [
                    "inspection_updated",
                    "inspection_failed",
                    "reconditioning_updated",
                    "reconditioning_failed",
                ]:
                    asyncio.run_coroutine_threadsafe(
                        manager.send(str(user_id), data),
                        loop,
                    )
                else:
                    logger.warning(
                        "Événement Redis inconnu : %s",
                        event,
                    )

            except Exception:
                logger.exception(
                    "Erreur lors du traitement d'un message Redis"
                )

    except Exception:
        logger.exception("Le listener Redis s'est arrêté")

    finally:
        pubsub.close()
