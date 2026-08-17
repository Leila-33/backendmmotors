from fastapi import APIRouter, Depends

from modules.auth.api.schemas import (
    CreateUserRequest,
    CreateUserResponse,
    FindUsersRequest,
    UserItemResponse,
    PaginatedUsersResponse,
    ToggleUserActiveRequest,
    ToggleUserActiveResponse,
    UpdateUserRoleRequest,
    UpdateUserRoleResponse,
    ArchiveUsersRequest,
    ArchiveUsersResponse,
    ArchiveUserResponse,
)

from modules.auth.api.dependencies import (
    get_create_user_usecase,
    get_find_users_usecase,
    get_update_user_role_usecase,
    get_toggle_user_active_usecase,
    get_archive_user_usecase,
    get_archive_users_usecase,
)

from modules.auth.application.dtos.admin.create_user_dto import (
    CreateUserDTO,
)
from modules.auth.application.dtos.admin.find_users_dto import (
    FindUsersDTO,
)
from modules.auth.application.dtos.admin.update_user_role_dto import (
    UpdateUserRoleDTO,
)
from modules.auth.application.dtos.admin.toggle_user_active_dto import (
    ToggleUserActiveDTO,
)
from modules.auth.application.dtos.admin.archive_users_dto import (
    ArchiveUsersDTO,
)

from modules.auth.application.use_cases.admin.create_user import (
    CreateUserUseCase,
)
from modules.auth.application.use_cases.admin.find_users import (
    FindUsersUseCase,
)
from modules.auth.application.use_cases.admin.update_user_role import (
    UpdateUserRoleUseCase,
)
from modules.auth.application.use_cases.admin.toggle_user_active import (
    ToggleUserActiveUseCase,
)
from modules.auth.application.use_cases.admin.archive_user import (
    ArchiveUserUseCase,
)
from modules.auth.application.use_cases.admin.archive_users import (
    ArchiveUsersUseCase,
)

from modules.auth.domain.entities.user import User

from core.security.dependencies import (
    get_current_admin,
)


router = APIRouter(
    tags=["Admin Auth"]
)


# =====================================================
# CREATE USER
# =====================================================

@router.post(
    "",
    response_model=CreateUserResponse,
)
def create_user(
    request: CreateUserRequest,
    usecase: CreateUserUseCase = Depends(
        get_create_user_usecase
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
):

    dto = CreateUserDTO(
        first_name=request.first_name,
        last_name=request.last_name,
        email=str(request.email),
        password=request.password,
        role=request.role,
    )

    result = usecase.execute(
        dto=dto,
        current_admin=current_admin,
    )

    return CreateUserResponse(
        id=result.id,
        email=result.email,
        role=result.role,
        message="Utilisateur créé avec succès",
    )


# =====================================================
# FIND USERS
# =====================================================
@router.get(
    "",
    response_model=PaginatedUsersResponse,
)
def find_users(
    request: FindUsersRequest = Depends(),
    usecase: FindUsersUseCase = Depends(
        get_find_users_usecase
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
):

    # =========================================
    # REQUEST → DTO
    # =========================================

    dto = FindUsersDTO(
        page=request.page,
        limit=request.limit,
        search=request.search,
        role=request.role,
        status=request.status,
        sort=request.sort,
    )

    # =========================================
    # USE CASE
    # =========================================

    result = usecase.execute(dto)

    # =========================================
    # RESULT → RESPONSE
    # =========================================

    return PaginatedUsersResponse(
        items=[
            UserItemResponse(
                id=item.id,
                first_name=item.first_name,
                last_name=item.last_name,
                email=item.email,
                role=item.role,
                is_active=item.is_active,
                is_deleted=item.is_deleted,
                is_verified=item.is_verified,
                created_at=item.created_at,
            )
            for item in result.items
        ],
        page=result.page,
        limit=result.limit,
        total=result.total,
        pages=result.pages,
    )

# =====================================================
# UPDATE USER ROLE
# =====================================================

@router.patch(
    "/{user_id}/role",
    response_model=UpdateUserRoleResponse,
)
def update_user_role(
    user_id: str,
    request: UpdateUserRoleRequest,
    usecase: UpdateUserRoleUseCase = Depends(
        get_update_user_role_usecase
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
):

    dto = UpdateUserRoleDTO(
        role=request.role,
    )

    result = usecase.execute(
        user_id=user_id,
        dto=dto,
        current_admin=current_admin,
    )

    return UpdateUserRoleResponse(
        id=result.id,
        role=result.role,
        message="Rôle mis à jour",
    )


# =====================================================
# TOGGLE USER ACTIVE
# =====================================================

@router.patch(
    "/{user_id}/active",
    response_model=ToggleUserActiveResponse,
)
def toggle_user_active(
    user_id: str,
    request: ToggleUserActiveRequest,
    usecase: ToggleUserActiveUseCase = Depends(
        get_toggle_user_active_usecase
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
):

    dto = ToggleUserActiveDTO(
        is_active=request.is_active,
    )

    result = usecase.execute(
        user_id=user_id,
        dto=dto,
        current_admin=current_admin,
    )

    return ToggleUserActiveResponse(
        id=result.id,
        is_active=result.is_active,
        message="Statut utilisateur mis à jour",
    )


# =====================================================
# ARCHIVE ONE USER
# =====================================================

@router.patch(
    "/{user_id}/archive",
    response_model=ArchiveUserResponse,
)
def archive_user(
    user_id: str,
    usecase: ArchiveUserUseCase = Depends(
        get_archive_user_usecase
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
):

    result = usecase.execute(
        user_id=user_id,
        current_admin=current_admin,
    )

    return ArchiveUserResponse(
        id=result.user_id,
        message="Utilisateur archivé",
    )


# =====================================================
# ARCHIVE MULTIPLE USERS
# =====================================================

@router.patch(
    "/archive",
    response_model=ArchiveUsersResponse,
)
def archive_users(
    request: ArchiveUsersRequest,
    usecase: ArchiveUsersUseCase = Depends(
        get_archive_users_usecase
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
):

    dto = ArchiveUsersDTO(
        user_ids=request.user_ids,
    )

    result = usecase.execute(
        dto=dto,
        current_admin=current_admin,
    )

    return ArchiveUsersResponse(
        archived_count=result.archived_count,
        user_ids=result.user_ids,
        message="Utilisateurs archivés avec succès"
    )