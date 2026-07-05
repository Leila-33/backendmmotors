from fastapi import Request, Depends
from modules.core.exceptions import TokenInvalid, TokenRevoked, Forbidden, TokenExpired
from modules.auth.domain.entities.user import UserRole
from modules.auth.api.dependencies import get_jwt_service
from modules.auth.api.dependencies import get_user_repository, get_blacklist_repository
from jwt import ExpiredSignatureError, InvalidTokenError

from fastapi import Request, Depends

from jwt import ExpiredSignatureError, InvalidTokenError

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