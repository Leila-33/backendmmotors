from modules.auth.application.use_cases.admin.find_users import FindUsersUseCase
from modules.auth.application.use_cases.admin.delete_user import DeleteUserUseCase
from modules.auth.application.use_cases.admin.update_user_role import UpdateUserRoleUseCase
from modules.auth.application.use_cases.admin.create_user import CreateUserUseCase
from modules.auth.application.use_cases.admin.toggle_user_active import ToggleUserActiveUseCase
from modules.auth.application.use_cases.admin.archive_user import ArchiveUserUseCase
from modules.auth.application.use_cases.admin.archive_users import ArchiveUsersUseCase

from modules.auth.domain.entities.user import User
from fastapi import APIRouter, Depends

from modules.auth.api.schemas import (
    FindUsersQuery,
    UpdateUserRoleSchema,
    CreateUserSchema,
    ToggleActiveSchema,
    ToggleUserActiveResponse,
    ArchiveUserResponse,
    ArchiveUsersSchema,
    ArchiveUsersResponse,
    PaginatedUsersResponse
)

from modules.auth.api.dependencies import (
    get_find_users_usecase,
    get_delete_user_usecase,
    get_update_user_role_usecase,
    get_create_user_usecase,
    get_toggle_active_usecase,
    get_archive_user_usecase,
    get_archive_users_usecase
)

from core.security.dependencies import get_current_admin

router = APIRouter(tags=["AdminAuth"])

@router.post("/")
def create_user(
    payload: CreateUserSchema,
    usecase: CreateUserUseCase = Depends(get_create_user_usecase),
    current_admin: User = Depends(get_current_admin)
):
    return usecase.execute(payload)



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


@router.patch("/{user_id}/role")
def update_user_role(
    user_id: str,
    payload: UpdateUserRoleSchema,
    usecase: UpdateUserRoleUseCase = Depends(get_update_user_role_usecase),
    current_admin: User = Depends(get_current_admin)
):
    return usecase.execute(user_id, payload.role)

@router.patch("/{user_id}/active", response_model=ToggleUserActiveResponse)
def toggle_active(
    user_id: str,
    payload: ToggleActiveSchema,
    usecase: ToggleUserActiveUseCase = Depends(get_toggle_active_usecase),
    current_admin: User = Depends(get_current_admin)
):
    return usecase.execute(user_id, payload.is_active)

@router.patch("/{user_id}/archive", response_model=ArchiveUserResponse)
def archive_user(
    user_id: str,
    usecase: ArchiveUserUseCase = Depends(get_archive_user_usecase),
    current_admin: User = Depends(get_current_admin)
):
    return usecase.execute(user_id)

@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    usecase: DeleteUserUseCase = Depends(get_delete_user_usecase),
    current_admin: User = Depends(get_current_admin)
):
    return usecase.execute(user_id)


@router.patch("/archive/bulk", response_model=ArchiveUsersResponse)
def archive_users(
    payload: ArchiveUsersSchema,
    usecase: ArchiveUsersUseCase = Depends(get_archive_users_usecase),
    current_admin: User = Depends(get_current_admin)
):
    return usecase.execute(payload.ids)