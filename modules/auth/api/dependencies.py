# app/modules/auth/dependencies.py

from fastapi import Depends

from core.dependencies import get_email_service

from modules.core.infrastructure.dependencies import (
    get_user_repository,
    get_refresh_repository,
    get_blacklist_repository,
    get_jwt_service

)
from modules.auth.application.use_cases.register_user import RegisterUser
from modules.auth.application.use_cases.login_user import LoginUser
from modules.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from modules.auth.application.use_cases.logout_user import LogoutUser
from modules.auth.application.use_cases.verify_email import VerifyEmail
from modules.auth.application.use_cases.admin.find_users import FindUsersUseCase
from modules.auth.application.use_cases.admin.delete_user import DeleteUserUseCase
from modules.auth.application.use_cases.admin.update_user_role import UpdateUserRoleUseCase
from modules.auth.application.use_cases.admin.create_user import CreateUserUseCase
from modules.auth.application.use_cases.admin.toggle_user_active import ToggleUserActiveUseCase
from modules.auth.application.use_cases.admin.archive_user import ArchiveUserUseCase
from modules.auth.application.use_cases.admin.archive_users import ArchiveUsersUseCase
from modules.auth.application.use_cases.admin.delete_user import DeleteUserUseCase

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


def get_find_users_usecase(
    user_repository=Depends(get_user_repository)
):
    return FindUsersUseCase(user_repository)

def get_delete_user_usecase(
    user_repository=Depends(get_user_repository)
):
    return DeleteUserUseCase(user_repository)



def get_update_user_role_usecase(
    user_repository=Depends(get_user_repository)
):
    return UpdateUserRoleUseCase(user_repository)


def get_create_user_usecase(
    user_repository=Depends(get_user_repository)
):
    return CreateUserUseCase(user_repository)

def get_toggle_active_usecase(
    user_repository=Depends(get_user_repository)
):
    return ToggleUserActiveUseCase(user_repository)

def get_archive_user_usecase(
    user_repository=Depends(get_user_repository)
):
    return ArchiveUserUseCase(user_repository)

def get_archive_users_usecase(
    user_repository=Depends(get_user_repository)
):
    return ArchiveUsersUseCase(user_repository)

def get_delete_user_usecase(
    user_repository=Depends(get_user_repository)
):
    return DeleteUserUseCase(user_repository)