# app/websocket/auth.py
import jwt
from fastapi import WebSocket
from modules.auth.domain.exceptions import TokenExpired, TokenInvalid

def get_user_from_ws_token(
    websocket: WebSocket,
    jwt_service,
    user_repo,
):

    token = websocket.query_params.get(
        "token"
    )

    if not token:
        return None


    try:

        payload = jwt_service.decode(
            token
        )

    except jwt.ExpiredSignatureError:
        raise TokenExpired()

    except jwt.InvalidTokenError:
        raise TokenInvalid()


    if payload.get("type") != "access":

        return None


    user_id = payload.get(
        "sub"
    )

    if not user_id:

        return None


    user = user_repo.get_by_id(
        user_id
    )


    if not user:

        return None


    if user.is_deleted:

        return None


    if not user.is_active:

        return None


    return user