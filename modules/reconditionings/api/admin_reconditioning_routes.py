from fastapi import (
    APIRouter,
    Depends,
    status,
)

from core.security.dependencies import get_current_admin

from modules.reconditionings.api.dependencies import (
    get_start_reconditioning_uc,
)

from modules.reconditionings.api.schemas import (
    StartReconditioningResponse,
)

from modules.reconditionings.application.dtos.admin.start_reconditioning_dto import (
    StartReconditioningDTO,
)

from modules.reconditionings.application.use_cases.admin.start_reconditioning import (
    StartReconditioningUseCase,
)
from modules.reconditionings.infrastructure.mapper.reconditioning_mapper import (
    ReconditioningMapper,
)

router = APIRouter(
    tags=["Reconditionings"]
)


# =====================================================
# START RECONDITIONING
# =====================================================

@router.post(
    "/{vehicle_id}/start",
    response_model=StartReconditioningResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_reconditioning(
    vehicle_id: str,
    current_admin=Depends(
        get_current_admin
    ),
    use_case: StartReconditioningUseCase = Depends(
        get_start_reconditioning_uc
    ),
):

    # =================================================
    # API → APPLICATION DTO
    # =================================================

    dto = StartReconditioningDTO(
        vehicle_id=vehicle_id,
        admin_id=current_admin.id,
    )

    # =================================================
    # APPLICATION
    # =================================================

    result = use_case.execute(dto)

    # =================================================
    # APPLICATION → API
    # =================================================

    return ReconditioningMapper.to_start_reconditioning_response(
        result
    )