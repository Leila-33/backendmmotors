from fastapi import APIRouter, Depends, HTTPException
# =========================
# AUTH
# =========================
from core.security.dependencies import get_current_admin

# =========================
# SCHEMAS
# =========================
from modules.vehicles.api.schemas import (
CreateVehicleRequest,
VehicleResponse,
UpdateVehicleRequest,
VehicleSearchFilters,
VehicleListResponse,
VehicleLifecycleDTO,
SetAvailabilityDTO
)

# =========================
# DEPENDENCIES (REPOSITORIES)
# =========================
from modules.vehicles.api.dependencies import(
    get_create_vehicle_use_case,
    get_update_vehicle_use_case,
    get_toggle_vehicle_type_uc,
    get_get_vehicles_admin_uc,
    get_delete_vehicle_use_case,
    get_vehicle_lifecycle_uc,
    get_final_check_uc,
    get_publish_vehicle_uc,
    get_set_availability_uc
) 

# =========================
# USE CASES
# =========================
from modules.vehicles.application.use_cases.admin.create_vehicle import CreateVehicle
from modules.vehicles.application.use_cases.admin.update_vehicle import UpdateVehicle
from modules.vehicles.application.use_cases.admin.toggle_vehicle_type import ToggleVehicleType
from modules.vehicles.application.use_cases.get_vehicles import GetVehiclesForAdminUseCase
from modules.vehicles.application.use_cases.admin.delete_vehicle import DeleteVehicle
from modules.vehicles.application.use_cases.admin.final_check import FinalCheckUseCase
from modules.vehicles.application.use_cases.admin.publish_vehicle import PublishVehicleUseCase
from modules.vehicles.application.use_cases.admin.set_availibity import SetAvailabilityUseCase
from modules.vehicles.application.use_cases.admin.get_vehicle_lifecycle import GetVehicleLifecycleUseCase


router = APIRouter(tags=["Admin Vehicles"])


# =========================
# ROUTE
# =========================
@router.post("/", response_model=VehicleResponse)
async def create_vehicle(
    request: CreateVehicleRequest,
    use_case: CreateVehicle = Depends(get_create_vehicle_use_case),
    current_admin=Depends(get_current_admin),
):
    return use_case.execute(request)

# =====================================================
#  UPDATE VEHICLE
# =====================================================
@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: str,
    data: UpdateVehicleRequest,
    use_case: UpdateVehicle = Depends(get_update_vehicle_use_case),
    current_admin=Depends(get_current_admin)
):
    return use_case.execute(
        vehicle_id=vehicle_id,
        data=data
    )

# =====================================================
#  TOGGLE TYPE (achat ↔ location)
# =====================================================
@router.patch("/{vehicle_id}/toggle-type", response_model=VehicleResponse)
def toggle_vehicle_type(
    vehicle_id: str,
    use_case: ToggleVehicleType = Depends(get_toggle_vehicle_type_uc),
    admin=Depends(get_current_admin)
):
    return use_case.execute(vehicle_id)

# =========================
# GET VEHICLES ADMIN
# =========================
@router.get("/", response_model=VehicleListResponse)
def get_vehicles_admin(
    filters: VehicleSearchFilters = Depends(),
    use_case: GetVehiclesForAdminUseCase = Depends(get_get_vehicles_admin_uc),
    admin=Depends(get_current_admin)
):
    return use_case.execute(filters)

# =========================
# DELETE VEHICLE
# =========================
@router.delete("/{vehicle_id}")
def delete_vehicle(
    vehicle_id: str,
    use_case: DeleteVehicle = Depends(get_delete_vehicle_use_case),
    current_admin=Depends(get_current_admin)
):
    return use_case.execute(vehicle_id)






@router.get(
    "/{vehicle_id}/lifecycle",
    response_model=VehicleLifecycleDTO
)
def get_lifecycle(
    vehicle_id: str,
    use_case: GetVehicleLifecycleUseCase = Depends(get_vehicle_lifecycle_uc),
    current_admin=Depends(get_current_admin)
):
        return use_case.execute(vehicle_id)

@router.post(
    "/{vehicle_id}/final-check"
)
def final_check(
    vehicle_id: str,
    uc: FinalCheckUseCase = Depends(
        get_final_check_uc
    ),
    current_admin=Depends(get_current_admin)
):

    return uc.execute(vehicle_id)

@router.post(
    "/{vehicle_id}/publish"
)
def publish_vehicle(
    vehicle_id: str,
    uc: PublishVehicleUseCase = Depends(
        get_publish_vehicle_uc
    ),
    current_admin=Depends(get_current_admin)
):
    return uc.execute(vehicle_id)


@router.patch("/{vehicle_id}/availability")
def set_availability(
    vehicle_id: str,
    dto: SetAvailabilityDTO,
    uc: SetAvailabilityUseCase = Depends(get_set_availability_uc),
    current_admin=Depends(get_current_admin)
):
    return uc.execute(vehicle_id, dto.value)