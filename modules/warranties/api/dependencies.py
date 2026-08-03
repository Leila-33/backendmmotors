
from fastapi import Depends
from modules.dependencies.dependencies import get_warranty_plan_repository

from modules.warranties.application.use_cases.admin.create_warranty_plan import CreateWarrantyPlanUseCase
from modules.warranties.application.use_cases.admin.get_warranty_plans import GetWarrantyPlansUseCase
from modules.warranties.application.use_cases.admin.toggle_warranty_plan import ToggleWarrantyPlanUseCase
from modules.warranties.application.use_cases.admin.update_warranty_plan import UpdateWarrantyPlanUseCase
from modules.warranties.application.use_cases.activate_vehicle_warranty import ActivateVehicleWarrantyUseCase

from core.database.dependencies import (
    get_unit_of_work
)


# =====================================================
# DEPENDENCY: USECASE
# =====================================================
def get_create_warranty_usecase(

    repository=Depends(
        get_warranty_plan_repository
    ),

    unit_of_work=Depends(
        get_unit_of_work
    ),

):

    return CreateWarrantyPlanUseCase(

        repository=repository,

        unit_of_work=unit_of_work,

    )



def get_get_warranty_plans_usecase(
    repo=Depends(get_warranty_plan_repository)
):

    return GetWarrantyPlansUseCase(repo)




def get_toggle_warranty_usecase(

    repository=Depends(
        get_warranty_plan_repository
    ),

    unit_of_work=Depends(
        get_unit_of_work
    ),

):

    return ToggleWarrantyPlanUseCase(

        repository=repository,

        unit_of_work=unit_of_work,

    )


def get_update_warranty_plan_usecase(

    repository=Depends(
        get_warranty_plan_repository
    ),

    unit_of_work=Depends(
        get_unit_of_work
    ),

):

    return UpdateWarrantyPlanUseCase(

        repository=repository,

        unit_of_work=unit_of_work,

    )

# =====================================================
# ACTIVATE VEHICLE WARRANTY
# =====================================================

def get_activate_vehicle_warranty_usecase(

    warranty_plan_repository=Depends(
        get_warranty_plan_repository
    ),

):

    return ActivateVehicleWarrantyUseCase(
        warranty_plan_repo=warranty_plan_repository
    )


