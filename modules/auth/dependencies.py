from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os

security = HTTPBearer()


class User:
    def __init__(self, id: str, is_admin: bool):
        self.id = id
        self.is_admin = is_admin


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"]
        )

        return User(
            id=payload.get("user_id"),
            is_admin=payload.get("is_admin", False)
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expiré")

    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token invalide")


def get_current_admin(user=Depends(get_current_user)):

    if not user.is_admin:
        raise HTTPException(403, "Admin only")

    return user