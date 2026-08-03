from modules.auth.application.use_cases.admin.find_users import FindUsersUseCase
from modules.auth.application.use_cases.admin.update_user_role import UpdateUserRoleUseCase
from modules.auth.application.use_cases.admin.create_user import CreateUserUseCase
from modules.auth.application.use_cases.admin.toggle_user_active import ToggleUserActiveUseCase
from modules.auth.application.use_cases.admin.archive_user import ArchiveUserUseCase
from modules.auth.application.use_cases.admin.archive_users import ArchiveUsersUseCase

from modules.auth.domain.entities.user import User
from fastapi import APIRouter, Depends

from modules.auth.api.schemas import (
    FindUsersQuery,
    UpdateUserRoleRequest,
    UpdateUserRoleResponse,
    CreateUserRequest,
    CreateUserResponse,
    ToggleUserActiveRequest,
    ToggleUserActiveResponse,
    ArchiveUserResponse,
    ArchiveUsersRequest,
    ArchiveUsersResponse,
    PaginatedUsersResponse
)

from modules.auth.api.dependencies import (
    get_find_users_usecase,
    get_update_user_role_usecase,
    get_create_user_usecase,
    get_toggle_user_active_usecase,
    get_archive_user_usecase,
    get_archive_users_usecase
)

from core.security.dependencies import get_current_admin

router = APIRouter(tags=["AdminAuth"])

@router.post(
    "/",
    response_model=CreateUserResponse,
)
def create_user(
    request: CreateUserRequest,
    use_case: CreateUserUseCase = Depends(
        get_create_user_usecase
    ),
):

    return use_case.execute(
        payload=request
    )



@router.get("/", response_model=PaginatedUsersResponse)
def get_users(
    page: int = 1,
    limit: int = 10,
    search: str = None,
    role: str = None,
    status: str = None,
    sort: str = "created_at_desc",
    usecase: FindUsersUseCase = Depends(get_find_users_usecase),
    current_admin: User = Depends(get_current_admin)
):

    query = FindUsersQuery(
        page=page,
        limit=limit,
        search=search,
        role=role,
        status=status,
        sort=sort
    )

    return usecase.execute(query)


@router.patch(
    "/{user_id}/role",
    response_model=UpdateUserRoleResponse
)
def update_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    uc: UpdateUserRoleUseCase = Depends(
        get_update_user_role_usecase
    ),
    current_admin: User = Depends(get_current_admin)
):

    return uc.execute(
        user_id=user_id,
        new_role=request.role
    )

@router.patch(
    "/{user_id}/active",
    response_model=ToggleUserActiveResponse
)
def toggle_user_active(
    user_id: str,
    request: ToggleUserActiveRequest,
    uc: ToggleUserActiveUseCase = Depends(
        get_toggle_user_active_usecase
    )
):

    return uc.execute(
        user_id=user_id,
        is_active=request.is_active
    )



@router.patch("/{user_id}/archive", response_model=ArchiveUserResponse)
def archive_user(
    user_id: str,
    usecase: ArchiveUserUseCase = Depends(get_archive_user_usecase),
    current_admin: User = Depends(get_current_admin)
):
    return usecase.execute(user_id)

@router.post(
    "/archive",
    response_model=ArchiveUsersResponse,
)
def archive_users(
    request: ArchiveUsersRequest,
    use_case: ArchiveUsersUseCase = Depends(
        get_archive_users_usecase
    ),
    current_admin: User = Depends(get_current_admin)
):

    return use_case.execute(
        ids=request.user_ids
    )
