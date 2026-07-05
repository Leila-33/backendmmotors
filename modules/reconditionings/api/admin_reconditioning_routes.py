from fastapi import APIRouter, Depends
from core.security.dependencies import get_current_admin

from modules.reconditionings.api.dependencies import (
    get_reconditioning_uc,
    get_start_reconditioning_uc
)
from modules.reconditionings.api.schemas import ReconditioningDTO
from modules.reconditionings.application.use_cases.admin.get_reconditioning import GetReconditioningUseCase
from modules.reconditionings.application.use_cases.admin.start_reconditioning import StartReconditioningUseCase

router = APIRouter(tags=["Reconditionings"])


@router.get("/{vehicle_id}", response_model=ReconditioningDTO)
def get_reconditioning(
    vehicle_id: str,
    use_case: GetReconditioningUseCase = Depends(get_reconditioning_uc),
    current_admin=Depends(get_current_admin)
):
    return use_case.execute(vehicle_id)




@router.post("/{vehicle_id}/start")
def start_reconditioning(
    vehicle_id: str,
    use_case: StartReconditioningUseCase = Depends(get_start_reconditioning_uc),
    current_admin=Depends(get_current_admin)
):

    return use_case.execute(vehicle_id, current_admin.id)