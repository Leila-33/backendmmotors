import asyncio
import json
import logging
from modules.vehicles.infrastructure.queue.redis_connection import redis_conn
from modules.notifications.application.services.websocket_manager import manager
logger = logging.getLogger(__name__)


def start_redis_listener(loop):
    pubsub = redis_conn.pubsub()

    pubsub.subscribe(
        "inspection_updates",
        "reconditioning_updates",
        "user_notifications",
    )

    print("🔥 Redis listener started")

    for message in pubsub.listen():
        if message["type"] != "message":
            continue

        try:
            data = json.loads(message["data"])
            channel = message["channel"]

            # Notifications WebSocket : SAV, compteurs, etc.
            if channel == "user_notifications":
                user_id = data.get("user_id")
                payload = data.get("message")

                if not user_id or not isinstance(payload, dict):
                    print("⚠️ Invalid user notification:", data)
                    continue

                asyncio.run_coroutine_threadsafe(
                    manager.send(str(user_id), payload),
                    loop,
                )
                continue

            # Inspections et reconditionnement : comportement existant
            event = data.get("event")
            user_id = data.get("user_id")

            if not user_id:
                print("⚠️ Missing user_id")
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
                print("⚠️ Unknown event:", event)

        except Exception:
            logger.exception("Erreur lors du traitement d'un message Redis")