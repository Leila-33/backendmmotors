from fastapi import APIRouter, Depends

from core.security.dependencies import get_current_admin
from modules.dependencies.dependencies import get_option_repository

from modules.options.application.use_cases.admin.create_option import CreateOptionUseCase
from modules.options.application.use_cases.admin.get_options import GetOptionsUseCase
from modules.options.application.use_cases.admin.update_option import UpdateOptionUseCase
from modules.options.application.use_cases.admin.toggle_options_status import ToggleOptionStatusUseCase

from modules.options.api.schemas import (
    CreateOptionRequest,
    CreateOptionResponse,
    UpdateOptionRequest,
    UpdateOptionResponse,
    OptionResponse,
    ToggleOptionStatusRequest
)
from modules.options.api.dependencies import (
    get_create_option_usecase,
    get_get_options_uc,
    get_update_option_uc,
    get_toggle_option_status_usecase
)

router = APIRouter(tags=["Admin - Options"])



# =========================
# CREATE
# =========================
@router.post("", response_model=CreateOptionResponse)
def create_option(
    request: CreateOptionRequest,
    uc: CreateOptionUseCase = Depends(get_create_option_usecase),
    admin=Depends(get_current_admin)
):
    return uc.execute(request)


# =========================
# GET ALL
# =========================
@router.get("", response_model=list[OptionResponse])
def get_all_options(
    uc: GetOptionsUseCase = Depends(get_get_options_uc),
    admin=Depends(get_current_admin)
):
    return uc.execute()


# =========================
# GET ACTIVE (clean)
# =========================
@router.get("/active", response_model=list[OptionResponse])
def get_active_options(
    repo=Depends(get_option_repository),
    admin=Depends(get_current_admin)
):
    return repo.get_active()


# =========================
# UPDATE
# =========================
@router.put("/{option_id}", response_model=UpdateOptionResponse)
def update_option(
    option_id: str,
    request: UpdateOptionRequest,
    uc: UpdateOptionUseCase = Depends(get_update_option_uc),
    admin=Depends(get_current_admin)
):
    return uc.execute(option_id, request)


# =========================
# TOGGLE    
# =========================
@router.patch(
    "/{option_id}/status",
    response_model=UpdateOptionResponse
)
def toggle_option_status(
    option_id: str,
    request: ToggleOptionStatusRequest,
    usecase: ToggleOptionStatusUseCase = Depends(
        get_toggle_option_status_usecase
    )
):

    return usecase.execute(
        option_id,
        request
    )