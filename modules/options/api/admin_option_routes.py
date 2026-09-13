from fastapi import APIRouter, Depends, status

from modules.auth.domain.entities.user import User

from core.security.dependencies import get_current_admin

from modules.options.api.schemas import (
    CreateOptionRequest,
    CreateOptionResponse,
    UpdateOptionRequest,
    UpdateOptionResponse,
    ToggleOptionStatusRequest,
    ToggleOptionStatusResponse,
    GetOptionsResponse,
)

from modules.options.api.dependencies import (
    get_create_option_usecase,
    get_get_options_usecase,
    get_get_active_options_usecase,
    get_update_option_usecase,
    get_toggle_option_status_usecase,
)

from modules.options.application.dtos.admin.create_option_dto import (
    CreateOptionDTO,
)
from modules.options.application.dtos.admin.update_option_dto import (
    UpdateOptionDTO,
)
from modules.options.application.dtos.admin.toggle_option_status_dto import (
    ToggleOptionStatusDTO,
)

from modules.options.application.use_cases.admin.create_option import (
    CreateOptionUseCase,
)
from modules.options.application.use_cases.admin.get_options import (
    GetOptionsUseCase,
)
from modules.options.application.use_cases.admin.get_active_options import (
    GetActiveOptionsUseCase,
)
from modules.options.application.use_cases.admin.update_option import (
    UpdateOptionUseCase,
)
from modules.options.application.use_cases.admin.toggle_option_status import (
    ToggleOptionStatusUseCase,
)

from modules.options.infrastructure.mapper.option_mapper import (
    OptionMapper,
)


router = APIRouter(
    tags=["Admin - Options"]
)


# =====================================================
# CREATE
# =====================================================

@router.post(
    "",
    response_model=CreateOptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_option(
    request: CreateOptionRequest,
    current_admin: User = Depends(
        get_current_admin
    ),
    usecase: CreateOptionUseCase = Depends(
        get_create_option_usecase
    ),
):

    dto = CreateOptionDTO(
        name=request.name,
        price=request.price,
        billing_type=request.billing_type,
        admin_id=current_admin.id,
    )

    result = usecase.execute(dto)

    return OptionMapper.to_create_response(
        result
    )


# =====================================================
# GET ALL
# =====================================================

@router.get(
    "",
    response_model=GetOptionsResponse,
)
def get_options(
    current_admin: User = Depends(
        get_current_admin
    ),
    usecase: GetOptionsUseCase = Depends(
        get_get_options_usecase
    ),
):

    result = usecase.execute()

    return OptionMapper.to_list_response(
        result
    )

# =====================================================
# GET ACTIVE OPTIONS
# =====================================================

@router.get(
    "/active",
    response_model=GetOptionsResponse,
)
def get_active_options(
    usecase: GetActiveOptionsUseCase = Depends(
        get_get_active_options_usecase
    ),
):

    result = usecase.execute()

    return OptionMapper.to_list_response(
        result
    )
# =====================================================
# UPDATE
# =====================================================

@router.put(
    "/{option_id}",
    response_model=UpdateOptionResponse,
)
def update_option(
    option_id: str,
    request: UpdateOptionRequest,
    current_admin: User = Depends(
        get_current_admin
    ),
    usecase: UpdateOptionUseCase = Depends(
        get_update_option_usecase
    ),
):

    dto = UpdateOptionDTO(
        option_id=option_id,
        name=request.name,
        price=request.price,
        billing_type=request.billing_type,
        admin_id=current_admin.id,
    )

    result = usecase.execute(dto)

    return OptionMapper.to_update_response(
        result
    )


# =====================================================
# TOGGLE STATUS
# =====================================================

@router.patch(
    "/{option_id}/status",
    response_model=ToggleOptionStatusResponse,
)
def toggle_option_status(
    option_id: str,
    request: ToggleOptionStatusRequest,
    current_admin: User = Depends(
        get_current_admin
    ),
    usecase: ToggleOptionStatusUseCase = Depends(
        get_toggle_option_status_usecase
    ),
):

    dto = ToggleOptionStatusDTO(
        option_id=option_id,
        is_active=request.is_active,
        admin_id=current_admin.id,
    )

    result = usecase.execute(dto)

    return OptionMapper.to_toggle_status_response(
        result
    )