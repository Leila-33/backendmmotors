from fastapi import APIRouter, WebSocket

router = APIRouter()
from modules.notifications.application.services.websocket_manager import ConnectionManager

manager = ConnectionManager()

@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):

    await manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()

    except Exception:
        manager.disconnect(user_id)