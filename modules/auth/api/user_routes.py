from fastapi import APIRouter, Depends, Request, Response, Cookie

from modules.auth.api.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    RefreshTokenResponse,
    VerifyEmailResponse,
    VerifyEmailRequest,
    LogoutResponse,
    UserResponse,
    CheckActivationTokenResponse,
    ActivateAccountRequest,
    ActivateAccountHttpResponse
)

from modules.auth.api.dependencies import (
    get_register_uc,
    get_login_uc,
    get_refresh_uc,
    get_logout_uc,
    get_verify_email_uc,
    get_check_activation_token_usecase,
    get_activate_account_usecase
    )

from modules.auth.application.use_cases.register_user import RegisterUser
from modules.auth.application.use_cases.login_user import LoginUser
from modules.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from modules.auth.application.use_cases.logout_user import LogoutUser
from modules.auth.application.use_cases.verify_email import VerifyEmail
from modules.auth.application.use_cases.check_activation_token import CheckActivationTokenUseCase
from modules.auth.application.use_cases.activate_account import ActivateAccountUseCase
from core.security.dependencies import get_current_user

from modules.auth.domain.exceptions import RefreshTokenMissing

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
@router.post(
    "/login",
    response_model=LoginResponse
)
def login(
    response: Response,
    request: LoginRequest,
    uc: LoginUser = Depends(get_login_uc)
):

    result = uc.execute(request)


    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=True,       # HTTPS production
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )


    return {
        "access_token": result["access_token"]
    }
# =========================
# REFRESH TOKEN
# =========================
@router.post(
    "/refresh",
    response_model=RefreshTokenResponse
)
def refresh(
    request: Request,
    response: Response,
    uc: RefreshTokenUseCase = Depends(
        get_refresh_uc
    )
):

    refresh_token = request.cookies.get(
        "refresh_token"
    )

    if not refresh_token:
        raise RefreshTokenMissing()

    result = uc.execute(
        refresh_token
    )

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=False,      # True en production (HTTPS)
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )

    return RefreshTokenResponse(
        access_token=result.access_token
    )
# =========================
# LOGOUT
# =========================
@router.post(
    "/logout",
    response_model=LogoutResponse
)
def logout(
    response: Response,
    refresh_token: str = Cookie(None),
    uc: LogoutUser = Depends(get_logout_uc)
):

    result = uc.execute(
        refresh_token
    )

    response.delete_cookie(
        "refresh_token"
    )

    return result


# =========================
# VERIFY EMAIL
# =========================
@router.get(
    "/verify-email",
    response_model=VerifyEmailResponse
)
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


# =========================
# CHECK ACTIVATION TOKEN
# =========================
@router.get("/activation/check", response_model=CheckActivationTokenResponse)
def check_activation_token(
    token: str,
    use_case: CheckActivationTokenUseCase = Depends(
        get_check_activation_token_usecase
    ),
):
    return use_case.execute(token)



# =========================
# ACTIVATE ACCOUNT
# =========================
@router.post(
    "/activate-account",
    response_model=ActivateAccountHttpResponse,
)
def activate_account(
    response: Response,
    request: ActivateAccountRequest,
    use_case: ActivateAccountUseCase = Depends(
        get_activate_account_usecase
    ),
):

    result = use_case.execute(
        request
    )


    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,

        httponly=True,

        secure=False,  # True en production HTTPS

        samesite="lax",

        max_age=60 * 60 * 24 * 7,
    )


    return ActivateAccountHttpResponse(
        message=result.message,

        access_token=result.access_token,

        redirect=result.redirect,
    )