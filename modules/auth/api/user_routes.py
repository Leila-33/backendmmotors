from fastapi import APIRouter, Cookie, Depends, Request, Response

from modules.auth.application.dtos.register_dto import RegisterDTO
from modules.auth.application.dtos.login_user_dto import LoginUserDTO
from modules.auth.application.dtos.activate_account_dto import (
    ActivateAccountDTO,
)

from modules.auth.api.schemas import (
    RegisterRequest,
    MessageResponse,
    LoginUserRequest,
    AccessTokenResponse,
    UserResponse,
    CheckActivationTokenResponse,
    ActivateAccountRequest,
    ActivateAccountResponse,
)

from modules.auth.api.dependencies import (
    get_register_user_usecase,
    get_login_user_usecase,
    get_refresh_token_usecase,
    get_logout_user_usecase,
    get_verify_email_usecase,
    get_check_activation_token_usecase,
    get_activate_account_usecase,
)

from modules.auth.application.use_cases.register_user import (
    RegisterUserUseCase,
)
from modules.auth.application.use_cases.login_user import (
    LoginUserUseCase,
)
from modules.auth.application.use_cases.refresh_token import (
    RefreshTokenUseCase,
)
from modules.auth.application.use_cases.logout_user import (
    LogoutUserUseCase,
)
from modules.auth.application.use_cases.verify_email import (
    VerifyEmailUseCase,
)
from modules.auth.application.use_cases.check_activation_token import (
    CheckActivationTokenUseCase,
)
from modules.auth.application.use_cases.activate_account import (
    ActivateAccountUseCase,
)

from core.security.dependencies import get_current_user

from modules.auth.domain.entities.user import User
from modules.auth.domain.exceptions import RefreshTokenMissing


router = APIRouter(
    tags=["auth"],
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=MessageResponse,
)
def register(
    data: RegisterRequest,
    usecase: RegisterUserUseCase = Depends(
        get_register_user_usecase
    ),
):
    dto = RegisterDTO(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=data.password,
        accepted_cgu=data.accepted_cgu,
    )

    result = usecase.execute(dto)

    return MessageResponse(
        message=result.message,
    )


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=AccessTokenResponse,
)
def login(
    request: LoginUserRequest,
    response: Response,
    usecase: LoginUserUseCase = Depends(
        get_login_user_usecase
    ),
):
    dto = LoginUserDTO(
        email=request.email,
        password=request.password,
    )

    result = usecase.execute(dto)

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=False,  # True en production HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return AccessTokenResponse(
        access_token=result.access_token,
    )


# ============================================================
# REFRESH TOKEN
# ============================================================

@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    usecase: RefreshTokenUseCase = Depends(
        get_refresh_token_usecase
    ),
):
    if not refresh_token:
        raise RefreshTokenMissing()

    result = usecase.execute(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return AccessTokenResponse(
        access_token=result.access_token,
    )

# ============================================================
# LOGOUT
# ============================================================

@router.post(
    "/logout",
    response_model=MessageResponse,
)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None
    ),
    usecase: LogoutUserUseCase = Depends(
        get_logout_user_usecase
    ),
):

    if refresh_token:

        usecase.execute(
            refresh_token
        )

    response.delete_cookie(
        key="refresh_token",
        path="/",
    )

    return MessageResponse(
        message="Déconnexion réussie",
    )

# ============================================================
# VERIFY EMAIL
# ============================================================

@router.get(
    "/verify-email",
    response_model=MessageResponse,
)
def verify_email(
    token: str,
    usecase: VerifyEmailUseCase = Depends(
        get_verify_email_usecase
    ),
):
    result = usecase.execute(
        token
    )

    return MessageResponse(
        message=result.message,
    )


# ============================================================
# ME
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    user: User = Depends(
        get_current_user
    ),
):
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role.value,
        is_verified=user.is_verified,
        first_name=user.first_name,
        last_name=user.last_name,
    )


# ============================================================
# CHECK ACTIVATION TOKEN
# ============================================================

@router.get(
    "/check-activation-token",
    response_model=CheckActivationTokenResponse,
)
def check_activation_token(
    token: str,
    usecase: CheckActivationTokenUseCase = Depends(
        get_check_activation_token_usecase
    ),
):
    result = usecase.execute(
        token
    )

    return CheckActivationTokenResponse(
        first_name=result.first_name,
        email=result.email,
        already_verified=result.already_verified,
        expired=result.expired,
    )


# ============================================================
# ACTIVATE ACCOUNT
# ============================================================

@router.post(
    "/activate-account",
    response_model=ActivateAccountResponse,
)
def activate_account(
    request: ActivateAccountRequest,
    response: Response,
    usecase: ActivateAccountUseCase = Depends(
        get_activate_account_usecase
    ),
):
    dto = ActivateAccountDTO(
        token=request.token,
        password=request.password,
        accepted_cgu=request.accepted_cgu,
    )

    result = usecase.execute(
        dto
    )

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=False,  # True en production HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
    )

    return ActivateAccountResponse(
        message=result.message,
        access_token=result.access_token,
        redirect=result.redirect,
    )