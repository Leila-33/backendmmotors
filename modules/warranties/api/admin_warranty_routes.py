from fastapi import APIRouter, Depends

from modules.warranties.application.use_cases.admin.create_warranty_plan import CreateWarrantyPlanUseCase
from modules.warranties.application.use_cases.admin.get_warranty_plans import GetWarrantyPlansUseCase
from modules.warranties.application.use_cases.admin.toggle_warranty_plan import ToggleWarrantyPlanUseCase
from modules.warranties.application.use_cases.admin.update_warranty_plan import UpdateWarrantyPlanUseCase

from modules.warranties.api.schemas import (
    CreateWarrantyPlanRequest,
    CreateWarrantyPlanResponse,
    WarrantyPlanResponse,
    ToggleWarrantyPlanRequest,
    UpdateWarrantyPlanResponse,
    UpdateWarrantyPlanRequest
)

router = APIRouter(tags=["Warranty Plans"])
from modules.warranties.api.dependencies import (
    get_create_warranty_usecase,
    get_get_warranty_plans_usecase,
    get_toggle_warranty_usecase,
    get_update_warranty_plan_usecase
    )
from core.security.dependencies import get_current_admin

# =====================================================
# CREATE WARRANTY PLAN
# =====================================================

@router.post("", response_model=CreateWarrantyPlanResponse)
def create_warranty_plan(

    dto: CreateWarrantyPlanRequest,
    current_admin=Depends(get_current_admin),
    usecase: CreateWarrantyPlanUseCase = Depends(get_create_warranty_usecase)

):

    return usecase.execute(dto, current_admin)
# =====================================================
# GET WARRANTY PLANS
# =====================================================
@router.get(
    "",
    response_model=list[WarrantyPlanResponse]
)
def get_warranty_plans(
    current_admin=Depends(get_current_admin),
    use_case: GetWarrantyPlansUseCase = Depends(
        get_get_warranty_plans_usecase
    )
):

    return use_case.execute()

@router.patch("/{plan_id}", response_model=UpdateWarrantyPlanResponse)
def toggle_warranty_plan(

    plan_id: str,
    request: ToggleWarrantyPlanRequest,
    usecase : ToggleWarrantyPlanUseCase = Depends(get_toggle_warranty_usecase),
    current_admin=Depends(get_current_admin)

):

    return usecase.execute(
        plan_id=plan_id,
        active=request.active,
        current_admin=current_admin
    )

@router.put(
    "/{plan_id}",
    response_model=UpdateWarrantyPlanResponse
)
def update_warranty_plan(
    plan_id: str,
    request: UpdateWarrantyPlanRequest,
    use_case: UpdateWarrantyPlanUseCase = Depends(get_update_warranty_plan_usecase),
    current_admin=Depends(get_current_admin)
):

    return use_case.execute(
        plan_id=plan_id,
        dto=request,
        current_admin=current_admin 
    )