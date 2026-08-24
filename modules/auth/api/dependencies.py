# app/modules/auth/dependencies.py

from fastapi import Depends

from core.email.dependencies import get_email_service
from core.security.dependencies import get_jwt_service
from modules.dependencies.dependencies import (
    get_user_repository,
    get_refresh_repository,
    get_user_activation_token_repository,
    get_lead_repository,
    get_event_service
)
from modules.auth.application.use_cases.register_user import RegisterUserUseCase
from modules.auth.application.use_cases.login_user import LoginUserUseCase
from modules.auth.application.use_cases.refresh_token import RefreshTokenUseCase
from modules.auth.application.use_cases.logout_user import LogoutUserUseCase
from modules.auth.application.use_cases.verify_email import VerifyEmailUseCase
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
from modules.auth.application.services.customer_account_service import CustomerAccountService
from modules.auth.application.services.user_creation_service import UserCreationService
from modules.auth.application.services.activation_token_service import ActivationTokenService
from modules.auth.application.services.activation_token_validator import ActivationTokenValidator
from core.security.jwt_service import JwtService

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
def get_register_user_usecase(
    user_creation_service=Depends(
        get_user_creation_service
    ),
    jwt_service=Depends(
        get_jwt_service
    ),
    email_service=Depends(
        get_email_service
    ),
    event_service=Depends(
        get_event_service
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return RegisterUserUseCase(
        user_creation_service,
        jwt_service,
        email_service,
        event_service,
        uow
    )

def get_login_user_usecase(
    user_repo=Depends(get_user_repository),
    refresh_repo=Depends(get_refresh_repository),
    jwt_service=Depends(get_jwt_service),
    uow=Depends(get_unit_of_work)
):

    return LoginUserUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        refresh_repo=refresh_repo,
        uow=uow
    )


def get_refresh_token_usecase(
    jwt=Depends(get_jwt_service),
    refresh_repo=Depends(get_refresh_repository),
    uow=Depends(get_unit_of_work)
):
    return RefreshTokenUseCase(
        refresh_repo=refresh_repo,
        jwt_service=jwt,
        uow=uow
    )


def get_logout_user_usecase(
    refresh_repo=Depends(get_refresh_repository),
    jwt_service=Depends(get_jwt_service),
    uow=Depends(get_unit_of_work)
):

    return LogoutUserUseCase(
        jwt_service=jwt_service,
        refresh_repository=refresh_repo,
        uow=uow
    )

def get_verify_email_usecase(
    user_repo=Depends(get_user_repository),
    jwt_service=Depends(get_jwt_service),
    event_service=Depends(
        get_event_service
    ),
    uow=Depends(get_unit_of_work)
):

    return VerifyEmailUseCase(
        user_repo=user_repo,
        jwt_service=jwt_service,
        event_service=event_service,
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
    event_service=Depends(
        get_event_service
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
        event_service=event_service,
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
    event_service=Depends(
        get_event_service
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return UpdateUserRoleUseCase(
        user_repo=user_repository,
        event_service=event_service,
        uow=uow,
    )



def get_toggle_user_active_usecase(
    user_repository=Depends(
        get_user_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return ToggleUserActiveUseCase(
        user_repo=user_repository,
        event_service=event_service,
        uow=uow,
    )

def get_archive_user_usecase(
    user_repository=Depends(
        get_user_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return ArchiveUserUseCase(
        user_repo=user_repository,
        event_service=event_service,
        uow=uow,
    )

def get_archive_users_usecase(
    user_repository=Depends(
        get_user_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return ArchiveUsersUseCase(
        user_repo=user_repository,
        event_service=event_service,
        uow=uow,
    )

def get_find_users_usecase(
    user_repository: UserRepository = Depends(
        get_user_repository
    ),
):
    return FindUsersUseCase(
        user_repo=user_repository
    )


def get_create_user_usecase(
    user_creation_service=Depends(
        get_user_creation_service
    ),
    event_service=Depends(
        get_event_service
    ),
    uow=Depends(
        get_unit_of_work
    ),
):

    return CreateUserUseCase(
        user_creation_service=user_creation_service,
        event_service=event_service,
        uow=uow,
    )







