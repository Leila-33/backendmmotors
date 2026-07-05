from fastapi import APIRouter, Depends

from modules.warranties.application.use_cases.admin.create_warranty_plan import CreateWarrantyPlanUseCase
from modules.warranties.application.use_cases.admin.get_warranty_plans import GetWarrantyPlansUseCase
from modules.warranties.api.schemas import (
    CreateWarrantyPlanDTO,
    ToggleWarrantyDTO
)

router = APIRouter(tags=["Warranty Plans"])
from modules.warranties.api.dependencies import (
    get_create_warranty_usecase,
    get_usecase,
    get_toggle_warranty_usecase
    )
from core.security.dependencies import get_current_admin

# =====================================================
# CREATE WARRANTY PLAN
# =====================================================

@router.post("")
def create_warranty_plan(

    dto: CreateWarrantyPlanDTO,
    current_admin=Depends(get_current_admin),
    usecase: CreateWarrantyPlanUseCase = Depends(get_create_warranty_usecase)

):

    return usecase.execute(dto)


@router.get("")
def get_plans(

    usecase: GetWarrantyPlansUseCase = Depends(get_usecase),

    admin=Depends(get_current_admin)

):

    return usecase.execute()

@router.patch("/{plan_id}")
def toggle_warranty_plan(

    plan_id: str,
    dto: ToggleWarrantyDTO,

    usecase=Depends(get_toggle_warranty_usecase),
    admin=Depends(get_current_admin)

):

    result = usecase.execute(
        plan_id=plan_id,
        active=dto.active
    )

    return {
        "success": True,
        "id": result.id,
        "active": result.active
    }