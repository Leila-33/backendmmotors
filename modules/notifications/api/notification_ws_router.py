from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from core.security.dependencies import get_current_user_websocket
from modules.auth.domain.entities.user import User
from modules.notifications.application.services.websocket_manager import manager


router = APIRouter()


@router.websocket("")
async def websocket_notifications(
    websocket: WebSocket,
    current_user: User = Depends(
        get_current_user_websocket
    ),
):
    user_id = str(current_user.id)

    await manager.connect(
        user_id=user_id,
        websocket=websocket,
    )

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(
            user_id=user_id,
            websocket=websocket,
        )

    except Exception:
        manager.disconnect(
            user_id=user_id,
            websocket=websocket,
        )
        raise
        