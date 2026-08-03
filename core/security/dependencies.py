from fastapi import Request, Depends
from modules.auth.domain.exceptions import TokenInvalid, Forbidden, TokenExpired
from modules.auth.domain.enums import UserRole
from modules.dependencies.dependencies import (
    get_user_repository,
)
from core.config.settings import settings
from core.security.jwt_service import JwtService
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError
)
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
):

    auth = request.headers.get(
        "Authorization"
    )

    if not auth:
        raise TokenInvalid()


    if not auth.startswith(
        "Bearer "
    ):
        raise TokenInvalid()


    token = auth.replace(
        "Bearer ",
        ""
    )


    try:

        payload = jwt_service.decode(
            token
        )


    except ExpiredSignatureError:

        raise TokenExpired()


    except InvalidTokenError:

        raise TokenInvalid()


    if payload.get("type") != "access":

        raise TokenInvalid()


    user = user_repo.get_by_id(
        payload.get("sub")
    )


    if not user:

        raise TokenInvalid()


    if user.is_deleted:

        raise Forbidden()


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
):

    auth = request.headers.get(
        "Authorization"
    )


    # =====================
    # VISITEUR NON CONNECTÉ
    # =====================

    if not auth:
        return None


    if not auth.startswith(
        "Bearer "
    ):
        return None


    token = auth.replace(
        "Bearer ",
        ""
    )


    # =====================
    # DECODE TOKEN
    # =====================

    try:

        payload = jwt_service.decode(
            token
        )


    except ExpiredSignatureError:

        return None


    except InvalidTokenError:

        return None



    # =====================
    # ACCESS TOKEN ONLY
    # =====================

    if payload.get("type") != "access":

        return None



    user_id = payload.get(
        "sub"
    )


    if not user_id:

        return None



    # =====================
    # USER
    # =====================

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