from fastapi import APIRouter, Depends

from modules.inspections.api.dependencies import (
    get_inspection_uc,
    get_start_inspection_uc

)
from modules.inspections.application.use_cases.admin.get_inspection import GetInspectionUseCase
from modules.inspections.application.use_cases.admin.start_inspection import StartInspectionUseCase
from core.security.dependencies import get_current_admin
from modules.inspections.api.schemas import (
    InspectionResponse,
    StartInspectionResponse
)
router = APIRouter(tags=["Inspections"])



@router.get("/{vehicle_id}", response_model=InspectionResponse)
def get_inspection(
    vehicle_id: str,
    use_case: GetInspectionUseCase = Depends(get_inspection_uc),
    current_admin=Depends(get_current_admin)
):
    return use_case.execute(vehicle_id)


@router.post("/{vehicle_id}/start", response_model=StartInspectionResponse)
def start_inspection(
    vehicle_id: str,
    use_case: StartInspectionUseCase = Depends(get_start_inspection_uc),
    current_admin=Depends(get_current_admin)
):

    return use_case.execute(vehicle_id, current_admin.id)
