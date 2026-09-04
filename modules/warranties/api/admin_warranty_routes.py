from fastapi import APIRouter, Depends, status

# =====================================================
# AUTH
# =====================================================

from core.security.dependencies import get_current_admin


# =====================================================
# API SCHEMAS
# =====================================================

from modules.warranties.api.schemas import (
    CreateWarrantyPlanRequest,
    WarrantyPlanActionResponse,
    WarrantyPlanResponse,
    ToggleWarrantyPlanRequest,
    UpdateWarrantyPlanRequest,
)


# =====================================================
# DTOs
# =====================================================

from modules.warranties.application.dtos.admin.create_warranty_plan_dto import (
    CreateWarrantyPlanDTO,
)

from modules.warranties.application.dtos.admin.toggle_warranty_plan_dto import (
    ToggleWarrantyPlanDTO,
)

from modules.warranties.application.dtos.admin.update_warranty_plan_dto import (
    UpdateWarrantyPlanDTO,
)


# =====================================================
# USE CASES
# =====================================================

from modules.warranties.application.use_cases.admin.create_warranty_plan import (
    CreateWarrantyPlanUseCase,
)

from modules.warranties.application.use_cases.admin.get_warranty_plans import (
    GetWarrantyPlansUseCase,
)

from modules.warranties.application.use_cases.admin.toggle_warranty_plan import (
    ToggleWarrantyPlanUseCase,
)

from modules.warranties.application.use_cases.admin.update_warranty_plan import (
    UpdateWarrantyPlanUseCase,
)


# =====================================================
# MAPPERS
# =====================================================

from modules.warranties.infrastructure.mappers.warranty_plan_mapper import (
    WarrantyPlanMapper,
)


# =====================================================
# DEPENDENCIES
# =====================================================

from modules.warranties.api.dependencies import (
    get_create_warranty_plan_usecase,
    get_get_warranty_plans_usecase,
    get_toggle_warranty_plan_usecase,
    get_update_warranty_plan_usecase,
)


# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    tags=["Warranty Plans"]
)


# =====================================================
# CREATE WARRANTY PLAN
# =====================================================

@router.post(
    "",
    response_model=WarrantyPlanActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_warranty_plan(
    request: CreateWarrantyPlanRequest,
    current_admin=Depends(get_current_admin),
    use_case: CreateWarrantyPlanUseCase = Depends(
        get_create_warranty_plan_usecase
    ),
):

    # API → APPLICATION

    dto = CreateWarrantyPlanDTO(
        name=request.name,
        description=request.description,
        plan_type=request.plan_type,
        duration_months=request.duration_months,
        mileage_limit=request.mileage_limit,
        covers_engine=request.covers_engine,
        covers_transmission=request.covers_transmission,
        covers_electronics=request.covers_electronics,
        covers_assistance=request.covers_assistance,
        covers_wear_parts=request.covers_wear_parts,
        price=request.price,
        admin_id=current_admin.id,
    )

    # APPLICATION

    result = use_case.execute(dto)

    # APPLICATION → API

    return WarrantyPlanActionResponse(
        id=result.plan_id,
        message="Plan de garantie créé avec succès",
    )


# =====================================================
# GET WARRANTY PLANS
# =====================================================

@router.get(
    "",
    response_model=list[WarrantyPlanResponse],
)
def get_warranty_plans(
    use_case: GetWarrantyPlansUseCase = Depends(
        get_get_warranty_plans_usecase
    ),
):

    # APPLICATION

    results = use_case.execute()

    # APPLICATION → API

    return [
        WarrantyPlanMapper.to_response(result)
        for result in results
    ]


# =====================================================
# TOGGLE WARRANTY PLAN
# =====================================================

@router.patch(
    "/{plan_id}/status",
    response_model=WarrantyPlanActionResponse,
)
def toggle_warranty_plan(
    plan_id: str,
    request: ToggleWarrantyPlanRequest,
    current_admin=Depends(get_current_admin),
    use_case: ToggleWarrantyPlanUseCase = Depends(
        get_toggle_warranty_plan_usecase
    ),
):

    # API → APPLICATION

    dto = ToggleWarrantyPlanDTO(
        plan_id=plan_id,
        active=request.active,
        admin_id=current_admin.id,
    )

    # APPLICATION

    result = use_case.execute(dto)

    # APPLICATION → API

    return WarrantyPlanActionResponse(
        id=result.id,
        message=(
            "Plan activé avec succès"
            if result.active
            else "Plan désactivé avec succès"
        ),
    )


# =====================================================
# UPDATE WARRANTY PLAN
# =====================================================

@router.put(
    "/{plan_id}",
    response_model=WarrantyPlanActionResponse,
)
def update_warranty_plan(
    plan_id: str,
    request: UpdateWarrantyPlanRequest,
    current_admin=Depends(get_current_admin),
    use_case: UpdateWarrantyPlanUseCase = Depends(
        get_update_warranty_plan_usecase
    ),
):

    # API → APPLICATION

    dto = UpdateWarrantyPlanDTO(
    plan_id=plan_id,
    admin_id=current_admin.id,
    **request.model_dump(),
)

    # APPLICATION

    result = use_case.execute(dto)

    # APPLICATION → API

    return WarrantyPlanActionResponse(
        id=result.id,
        message="Plan modifié avec succès",
    )