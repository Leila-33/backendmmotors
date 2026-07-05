# app/modules/auth/routes.py

from fastapi import APIRouter, Depends, Request, Response

from modules.auth.api.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshResponse,
    VerifyEmailRequest,
    LogoutRequest,
    UserResponse,
)

from modules.auth.api.dependencies import (
    get_register_uc,
    get_login_uc,
    get_refresh_uc,
    get_logout_uc,
    get_verify_email_uc
    )

from modules.auth.application.use_cases.register_user import RegisterUser
from modules.auth.application.use_cases.login_user import LoginUser
from modules.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from modules.auth.application.use_cases.logout_user import LogoutUser
from modules.auth.application.use_cases.verify_email import VerifyEmail


from core.security.dependencies import get_current_user

from modules.core.exceptions import RefreshTokenMissing, Unauthorized

router = APIRouter(tags=["auth"])


# =========================
# REGISTER
# =========================
@router.post("/register", response_model=RegisterResponse)
def register(
    request: RegisterRequest,
    uc: RegisterUser = Depends(get_register_uc)
):
    return uc.execute(request)


# =========================
# LOGIN
# =========================
from fastapi import Response

@router.post("/login", response_model=LoginResponse)
def login(
    response: Response,
    request: LoginRequest,
    uc: LoginUser = Depends(get_login_uc)
):
    result= uc.execute(request)

    # 🔥 SET COOKIE
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,   # ⚠️ True en prod (HTTPS)
        samesite="lax",
        max_age=60 * 60 * 24 * 7  # 7 jours
    )

    return {
    "access_token": result["access_token"],
    "refresh_token": result["refresh_token"]
}
# =========================
# REFRESH TOKEN
# =========================
@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    request: Request,
    response: Response,
    uc: RefreshTokenUseCase = Depends(get_refresh_uc)
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise RefreshTokenMissing()

    result = uc.execute(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,  # ⚠️ mettre True en prod
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
    }
# =========================
# LOGOUT
# =========================
@router.post("/logout")
def logout(
    request: LogoutRequest,
    response: Response,
    uc: LogoutUser = Depends(get_logout_uc)
):
    if not request.token:
        raise Unauthorized()

    response.delete_cookie("refresh_token")

    return uc.execute(request.token)


# =========================
# VERIFY EMAIL
# =========================
@router.post("/verify-email")
def verify_email(
    request: VerifyEmailRequest,
    uc: VerifyEmail = Depends(get_verify_email_uc)
):
    return uc.execute(request.token)


# =========================
# ME (AUTH USER)
# =========================
@router.get("/me", response_model=UserResponse)
def me(
    user=Depends(get_current_user)
):
    return user
