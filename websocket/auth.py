# app/websocket/auth.py

from fastapi import WebSocket


def get_user_from_ws_token(
    websocket: WebSocket,
    jwt_service,
    user_repo,
    blacklist_repo
):

    token = websocket.query_params.get("token")

    if not token:
        return None

    if blacklist_repo.exists(token):
        return None

    try:
        payload = jwt_service.decode(token)
    except Exception:
        return None

    user = user_repo.get_by_id(payload["sub"])

    if not user or not user.is_active:
        return None

    return user