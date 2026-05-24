from modules.auth.application.use_cases.admin.get_users import GetUsersUseCase
from fastapi import APIRouter, Depends, Request, Response, Query

from modules.auth.api.schemas import (
    GetUsersDTO
)

from modules.auth.api.dependencies import (
    get_users_usecase

)

from core.security.dependencies import get_current_admin

router = APIRouter(tags=["AdminAuth"])

@router.get("")
def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = None,
    role: str | None = None,
    usecase: GetUsersUseCase = Depends(get_users_usecase),
    current_admin=Depends(get_current_admin)
):

    dto = GetUsersDTO(
        page=page,
        limit=limit,
        search=search,
        role=role
    )

    return usecase.execute(dto)