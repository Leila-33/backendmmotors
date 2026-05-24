# app/modules/auth/dependencies.py

from fastapi import Depends

from core.security.jwt_service import JwtService
from core.config import settings


from modules.auth.application.use_cases.register_user import RegisterUser
from modules.auth.application.use_cases.login_user import LoginUser
from modules.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from modules.auth.application.use_cases.logout_user import LogoutUser
from modules.auth.application.use_cases.verify_email import VerifyEmail

from modules.auth.infrastructure.repositories.user_repository_sql import UserRepositorySQL

from infrastructure.db.dependencies import get_db


# =========================
# BASE SERVICES
# =========================

def get_jwt_service():
    return JwtService(
        secret=settings.JWT_SECRET,
        algorithm="HS256"
    )


from modules.auth.infrastructure.repositories.user_repository_sql import UserRepositorySQL
from modules.auth.infrastructure.repositories.refresh_repository_sql import RefreshRepositorySQL
from modules.auth.infrastructure.repositories.blacklist_repository_sql import BlacklistRepositorySQL
from core.dependencies import get_email_service


def get_user_repository(db=Depends(get_db)):
    return UserRepositorySQL(db)

def get_refresh_repository(db=Depends(get_db)):
    return RefreshRepositorySQL(db)


def get_blacklist_repository(db=Depends(get_db)):
    return BlacklistRepositorySQL(db)

def get_user_repository(db=Depends(get_db)):
    return UserRepositorySQL(db)
# =========================
# USE CASES
# =========================

def get_register_uc(
    user_repo=Depends(get_user_repository),
    jwt=Depends(get_jwt_service),
    email=Depends(get_email_service)
):
    return RegisterUser(user_repo, jwt, email)


def get_login_uc(
    user_repo=Depends(get_user_repository),
    jwt=Depends(get_jwt_service),
    refresh_repo=Depends(get_refresh_repository)
):
    return LoginUser(user_repo, jwt, refresh_repo)


def get_refresh_uc(
    jwt=Depends(get_jwt_service),
    refresh_repo=Depends(get_refresh_repository),
    blacklist_repo=Depends(get_blacklist_repository)
):
    return RefreshTokenUseCase(
        refresh_repo=refresh_repo,
        blacklist_repo=blacklist_repo,
        jwt_service=jwt
    )


def get_logout_uc(
    blacklist=Depends(get_blacklist_repository)
):
    return LogoutUser(blacklist)


def get_verify_email_uc(
    user_repo=Depends(get_user_repository),
    jwt=Depends(get_jwt_service)
):
    return VerifyEmail(user_repo, jwt)


# dependencies/users.py

# dependencies/usecases.py

from fastapi import Depends
from modules.auth.application.use_cases.admin.get_users import GetUsersUseCase


def get_users_usecase(
    user_repository=Depends(get_user_repository)
):
    return GetUsersUseCase(user_repository)