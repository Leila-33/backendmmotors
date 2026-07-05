
from fastapi import Depends
from modules.core.infrastructure.dependencies import get_warranty_plan_repository

from modules.warranties.application.use_cases.admin.create_warranty_plan import CreateWarrantyPlanUseCase
from modules.warranties.application.use_cases.admin.get_warranty_plans import GetWarrantyPlansUseCase
from modules.warranties.application.use_cases.admin.toggle_warranty_plan import ToggleWarrantyPlanUseCase

# =====================================================
# DEPENDENCY: USECASE
# =====================================================

def get_create_warranty_usecase(
    repo=Depends(get_warranty_plan_repository)
):

    return CreateWarrantyPlanUseCase(repo)


def get_usecase(
    repo=Depends(get_warranty_plan_repository)
):

    return GetWarrantyPlansUseCase(repo)


def get_toggle_warranty_usecase(
    repo=Depends(get_warranty_plan_repository)
):

    return ToggleWarrantyPlanUseCase(repo)

