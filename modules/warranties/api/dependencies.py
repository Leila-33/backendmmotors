
from fastapi import Depends

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
from modules.warranties.application.use_cases.activate_vehicle_warranty import (
    ActivateVehicleWarrantyUseCase,
)

# =====================================================
# CORE
# =====================================================

from core.database.dependencies import get_unit_of_work

# =====================================================
# SHARED DEPENDENCIES
# =====================================================

from modules.dependencies.dependencies import (
    get_event_service,
    get_vehicle_repository,
    get_vehicle_warranty_repository,
    get_warranty_plan_repository,
)


# =====================================================
# ADMIN - CREATE WARRANTY PLAN
# =====================================================

def get_create_warranty_plan_usecase(
    repository=Depends(
        get_warranty_plan_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return CreateWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# =====================================================
# ADMIN - GET WARRANTY PLANS
# =====================================================

def get_get_warranty_plans_usecase(
    repository=Depends(
        get_warranty_plan_repository
    ),
):
    return GetWarrantyPlansUseCase(
        repository=repository,
    )


# =====================================================
# ADMIN - TOGGLE WARRANTY PLAN
# =====================================================

def get_toggle_warranty_plan_usecase(
    repository=Depends(
        get_warranty_plan_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return ToggleWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# =====================================================
# ADMIN - UPDATE WARRANTY PLAN
# =====================================================

def get_update_warranty_plan_usecase(
    repository=Depends(
        get_warranty_plan_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return UpdateWarrantyPlanUseCase(
        repository=repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# =====================================================
# ACTIVATE VEHICLE WARRANTY
# =====================================================

def get_activate_vehicle_warranty_usecase(
        vehicle_repository=Depends(
            get_vehicle_repository
        ),
    warranty_repository=Depends(
        get_vehicle_warranty_repository
    ),
    warranty_plan_repository=Depends(
        get_warranty_plan_repository
    ),
    event_service=Depends(get_event_service)

):

    return ActivateVehicleWarrantyUseCase(
        vehicle_repository=vehicle_repository,
        warranty_repository=warranty_repository,
        warranty_plan_repository=warranty_plan_repository,
        event_service=event_service,
    )










