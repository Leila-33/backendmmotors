from fastapi import APIRouter, Depends

from modules.inspections.api.dependencies import (
    get_get_inspection_usecase,
    get_start_inspection_usecase,
)

from modules.auth.domain.entities.user import User

from modules.inspections.infrastructure.mappers.inspection_mapper import (
    InspectionMapper,
)


from modules.inspections.application.use_cases.admin.get_inspection import (
    GetInspectionUseCase,
)

from modules.inspections.application.use_cases.admin.start_inspection import (
    StartInspectionUseCase,
)

from core.security.dependencies import get_current_admin

from modules.inspections.api.schemas import (
    InspectionResponse,
    StartInspectionResponse,
)


router = APIRouter(
    tags=["Inspections"]
)



@router.get(
    "/{vehicle_id}",
    response_model=InspectionResponse,
)
def get_inspection(
    vehicle_id: str,
    usecase: GetInspectionUseCase = Depends(
        get_get_inspection_usecase
    ),
):
    result = usecase.execute(
        vehicle_id=vehicle_id
    )

    return InspectionMapper.to_response(
        result
    )


@router.post(
    "/{vehicle_id}/start",
    response_model=StartInspectionResponse,
)
def start_inspection(
    vehicle_id: str,
    current_admin: User = Depends(
        get_current_admin
    ),
    usecase: StartInspectionUseCase = Depends(
        get_start_inspection_usecase
    ),
):
    result = usecase.execute(
        vehicle_id=vehicle_id,
        admin_id=current_admin.id,
    )

    return InspectionMapper.start(
        result
    )