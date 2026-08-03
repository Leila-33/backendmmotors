# app/modules/auth/dependencies.py

from fastapi import Depends

from core.email.dependencies import get_email_service
from core.security.dependencies import get_jwt_service
from modules.dependencies.dependencies import (
    get_user_repository,
    get_refresh_repository,
    get_user_activation_token_repository,
    get_lead_repository
)
from modules.auth.application.use_cases.register_user import RegisterUser
from modules.auth.application.use_cases.login_user import LoginUser
from modules.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from modules.auth.application.use_cases.logout_user import LogoutUser
from modules.auth.application.use_cases.verify_email import VerifyEmail
from modules.auth.application.use_cases.admin.find_users import FindUsersUseCase
from modules.auth.application.use_cases.admin.update_user_role import UpdateUserRoleUseCase
from modules.auth.application.use_cases.admin.create_user import CreateUserUseCase
from modules.auth.application.use_cases.admin.toggle_user_active import ToggleUserActiveUseCase
from modules.auth.application.use_cases.admin.archive_user import ArchiveUserUseCase
from modules.auth.application.use_cases.admin.archive_users import ArchiveUsersUseCase
from modules.auth.application.use_cases.activate_account import ActivateAccountUseCase
from modules.auth.application.use_cases.check_activation_token import CheckActivationTokenUseCase

# =========================
# CORE
# =========================
from core.database.dependencies import (
    get_unit_of_work
)
from core.database.unit_of_work import UnitOfWork

# =========================
# SERVICES
# =========================
from modules.auth.application.services.customer_account_service import CustomerAccountService
from modules.auth.application.services.user_creation_service import UserCreationService
from modules.auth.application.services.activation_token_service import ActivationTokenService
from modules.auth.application.services.activation_token_validator import ActivationTokenValidator
from core.security.jwt_service import JwtService

# =========================
# REPOSITORY
# =========================
from modules.auth.domain.repositories.user_repository import UserRepository
from modules.auth.domain.repositories.user_activation_token_repository import UserActivationTokenRepository
from modules.auth.domain.repositories.refresh_token_repository import RefreshTokenRepository
from modules.leads.domain.repositories.lead_repository import LeadRepository

# =========================
# SERVICES
# =========================
def get_user_creation_service(
    user_repository=Depends(get_user_repository)
):
    return UserCreationService(user_repository)

def get_activation_token_service(
    user_activation_token_repository=Depends(get_user_activation_token_repository)
):
    return ActivationTokenService(user_activation_token_repository)


def get_customer_account_service(
    
    user_creation_service : UserCreationService = Depends(get_user_creation_service),

    activation_token_service: ActivationTokenService = Depends(
        get_activation_token_service,
    ),
    lead_repository : LeadRepository = Depends(get_lead_repository)

):

    return CustomerAccountService(

        user_creation_service=user_creation_service,

        activation_token_service=activation_token_service,
        lead_repository=lead_repository
    )


def get_activation_token_validator(

    activation_token_repository: UserActivationTokenRepository = Depends(
        get_user_activation_token_repository,
    ),

):

    return ActivationTokenValidator(

        activation_token_repository
    )


# =========================
# USE CASES CLIENT
# =========================
def get_register_uc(
    user_creation_service : UserCreationService = Depends(get_user_creation_service),
    jwt=Depends(get_jwt_service),
    email=Depends(get_email_service),
    uow=Depends(get_unit_of_work)
):
    return RegisterUser(
        user_creation_service=user_creation_service,
        jwt_service=jwt,
        email_service=email,
        uow=uow
 )


def get_login_uc(
    user_repo=Depends(get_user_repository),
    refresh_repo=Depends(get_refresh_repository),
    jwt_service=Depends(get_jwt_service),
    uow=Depends(get_unit_of_work)
):

    return LoginUser(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow
    )


def get_refresh_uc(
    jwt=Depends(get_jwt_service),
    refresh_repo=Depends(get_refresh_repository),
    uow=Depends(get_unit_of_work)
):
    return RefreshTokenUseCase(
        refresh_repo=refresh_repo,
        jwt_service=jwt,
        uow=uow
    )


def get_logout_uc(
    refresh_repo=Depends(get_refresh_repository),
    jwt_service=Depends(get_jwt_service),
    uow=Depends(get_unit_of_work)
):

    return LogoutUser(
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow
    )

def get_verify_email_uc(
    user_repo=Depends(get_user_repository),
    jwt_service=Depends(get_jwt_service),
    uow=Depends(get_unit_of_work)
):

    return VerifyEmail(
        user_repo=user_repo,
        jwt_service=jwt_service,
        uow=uow
    )


def get_activate_account_usecase(

    validator: ActivationTokenValidator = Depends(
        get_activation_token_validator,
    ),

    activation_token_repository: UserActivationTokenRepository = Depends(
        get_user_activation_token_repository,
    ),

    user_repository: UserRepository = Depends(
        get_user_repository,
    ),
    refresh_repository : RefreshTokenRepository = Depends(get_refresh_repository),

    jwt_service: JwtService = Depends(
        get_jwt_service,
    ),
    uow=Depends(get_unit_of_work)
):

    return ActivateAccountUseCase(

        validator=validator,

        activation_token_repository=(
            activation_token_repository
        ),

        user_repository=user_repository,
        refresh_repository=refresh_repository,


        jwt_service=jwt_service,
        uow=uow
    )


def get_check_activation_token_usecase(

    validator: ActivationTokenValidator = Depends(
        get_activation_token_validator,
    ),

    user_repository: UserRepository = Depends(
        get_user_repository,
    ),

):

    return CheckActivationTokenUseCase(

        validator=validator,

        user_repository=user_repository
    )







# =========================
# USE CASES ADMIN
# =========================
def get_update_user_role_usecase(
    user_repository=Depends(
        get_user_repository
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return UpdateUserRoleUseCase(
        user_repo=user_repository,
        uow=uow,
    )



def get_toggle_user_active_usecase(
    user_repository=Depends(
        get_user_repository
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return ToggleUserActiveUseCase(
        user_repo=user_repository,
        uow=uow,
    )

def get_archive_user_usecase(
    user_repository=Depends(
        get_user_repository
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return ArchiveUserUseCase(
        user_repo=user_repository,
        uow=uow,
    )

def get_archive_users_usecase(
    user_repository=Depends(
        get_user_repository
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return ArchiveUsersUseCase(
        user_repo=user_repository,
        uow=uow,
    )


def get_find_users_usecase(
    user_repository=Depends(get_user_repository)
):
    return FindUsersUseCase(user_repository)


def get_create_user_usecase(
    user_creation_service=Depends(
        get_user_creation_service
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return CreateUserUseCase(
        user_creation_service=user_creation_service,
        uow=uow,
    )







