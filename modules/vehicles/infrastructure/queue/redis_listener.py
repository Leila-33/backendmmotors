import asyncio
import json
from modules.vehicles.infrastructure.queue.redis_connection import redis_conn
from modules.notifications.application.services.websocket_manager import manager


import json
import asyncio

def start_redis_listener(loop):
    pubsub = redis_conn.pubsub()

    pubsub.subscribe(
        "inspection_updates",
        "reconditioning_updates"
    )

    print("🔥 Redis listener started")

    for message in pubsub.listen():

        if message["type"] != "message":
            continue

        data = json.loads(message["data"])

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
                manager.send(user_id, data),
                loop
            )
        else:
            print("⚠️ Unknown event:", event)