from fastapi import Request, Depends
from modules.auth.domain.exceptions import TokenInvalid, TokenRevoked, Forbidden, TokenExpired
from modules.auth.domain.enums import UserRole
from modules.dependencies.dependencies import (
    get_user_repository,
    get_blacklist_repository
)
from jwt import ExpiredSignatureError, InvalidTokenError
from core.config.settings import settings
from core.security.jwt_service import JwtService

from fastapi import Request, Depends

def get_jwt_service():
    return JwtService(
        secret=settings.JWT_SECRET,
        algorithm="HS256",
    )

def get_current_user(
    request: Request,
    jwt_service=Depends(get_jwt_service),
    user_repo=Depends(get_user_repository),
    blacklist_repo=Depends(get_blacklist_repository)
):

    auth = request.headers.get("Authorization")

    if not auth:
        raise TokenInvalid()

    token = auth.replace("Bearer ", "")

    if blacklist_repo.exists(token):
        raise TokenRevoked()

    try:
        payload = jwt_service.decode(token)

    except ExpiredSignatureError:
        raise TokenExpired()  # ✅ ICI

    except InvalidTokenError:
        raise TokenInvalid()  # ✅ ICI

    user = user_repo.get_by_id(payload["sub"])

    if not user:
        raise TokenInvalid()

    if not user.is_active:
        raise Forbidden()
    return user



def get_current_admin(
    current_user=Depends(get_current_user)
):

    if current_user.role != UserRole.ADMIN:
        raise Forbidden()
    return current_user


def get_current_sav_agent(
    current_user=Depends(get_current_user)
):

    if current_user.role != UserRole.SAV_AGENT:
        raise Forbidden()
    return current_user

def get_current_sales_agent(
    current_user=Depends(get_current_user)
):

    if current_user.role != UserRole.SALES_AGENT:
        raise Forbidden()
    return current_user





def get_optional_current_user(
    request: Request,
    jwt_service=Depends(get_jwt_service),
    user_repo=Depends(get_user_repository),
    blacklist_repo=Depends(get_blacklist_repository)
):

    auth = request.headers.get("Authorization")


    # Visiteur non connecté
    if not auth:
        return None


    token = auth.replace(
        "Bearer ",
        ""
    )


    # Token révoqué
    if blacklist_repo.exists(token):
        return None


    try:

        payload = jwt_service.decode(
            token
        )


    except ExpiredSignatureError:

        return None


    except InvalidTokenError:

        return None



    user = user_repo.get_by_id(
        payload.get("sub")
    )


    if not user:
        return None


    if not user.is_active:
        return None


    return user