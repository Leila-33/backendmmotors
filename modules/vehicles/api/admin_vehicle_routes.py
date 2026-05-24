from fastapi import APIRouter, Depends
from fastapi import Form
from typing import Optional
import json
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
)
from modules.core.enums import VehicleType, VehicleCondition, EngineType

# =========================
# DEPENDENCIES (REPOSITORIES)
# =========================
from modules.vehicles.api.dependencies import(
    get_create_vehicle_use_case,
    get_update_vehicle_use_case,
    get_toggle_vehicle_type_uc,
    get_get_vehicles_admin_uc,
    get_delete_vehicle_use_case
) 

# =========================
# ERRORS
# =========================
from modules.core.exceptions import(
    InvalidJSON,
    InvalidListFormat
) 
# =========================
# USE CASES
# =========================
from modules.vehicles.application.use_cases.admin.create_vehicle import CreateVehicle
from modules.vehicles.application.use_cases.admin.update_vehicle import UpdateVehicle
from modules.vehicles.application.use_cases.admin.toggle_vehicle_type import ToggleVehicleType
from modules.vehicles.application.use_cases.get_vehicles import GetVehiclesForAdminUseCase
from modules.vehicles.application.use_cases.admin.delete_vehicle import DeleteVehicle

router = APIRouter(tags=["Admin Vehicles"])

# =====================================================
#  CREATE VEHICLE
# =====================================================
from fastapi import APIRouter, Depends, Form, File, UploadFile
from typing import List, Optional
import json

router = APIRouter()


from fastapi import APIRouter, Depends, Form, File, UploadFile
from typing import List, Optional
import json





router = APIRouter(tags=["Admin Vehicles"])





# =========================
# ROUTE
# =========================
@router.post("/", response_model=VehicleResponse)
async def create_vehicle(
    request: CreateVehicleRequest,   # 👈 JSON BODY
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
    current_admin=Depends(get_current_admin),
):
    return use_case.execute(vehicle_id)