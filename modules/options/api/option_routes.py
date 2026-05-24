from fastapi import APIRouter, Depends

from core.security.dependencies import get_current_admin
from modules.options.api.dependencies import get_option_repository

from modules.options.application.use_cases.create_option import CreateOption
from modules.options.application.use_cases.get_options import GetOptions
from modules.options.application.use_cases.update_option import UpdateOption
from modules.options.application.use_cases.delete_option import DeleteOption

from modules.options.api.schemas import (
    CreateOptionRequest,
    UpdateOptionRequest,
    OptionResponse
)
from modules.options.api.dependencies import (
    get_create_option_uc,
    get_get_options_uc,
    get_update_option_uc,
    get_delete_option_uc
)

router = APIRouter(tags=["Admin - Options"])



# =========================
# CREATE
# =========================
@router.post("/", response_model=OptionResponse)
def create_option(
    request: CreateOptionRequest,
    uc: CreateOption = Depends(get_create_option_uc),
    admin=Depends(get_current_admin)
):
    return uc.execute(request)


# =========================
# GET ALL
# =========================
@router.get("/", response_model=list[OptionResponse])
def get_all_options(
    uc: GetOptions = Depends(get_get_options_uc),
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
@router.put("/{option_id}", response_model=OptionResponse)
def update_option(
    option_id: str,
    request: UpdateOptionRequest,
    uc: UpdateOption = Depends(get_update_option_uc),
    admin=Depends(get_current_admin)
):
    return uc.execute(option_id, request)


# =========================
# DELETE
# =========================
@router.delete("/{option_id}")
def delete_option(
    option_id: str,
    uc: DeleteOption = Depends(get_delete_option_uc),
    admin=Depends(get_current_admin)
):
    uc.execute(option_id)

    return {"message": "Option désactivée avec succès"}