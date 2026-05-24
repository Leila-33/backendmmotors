from fastapi import APIRouter, Depends

# =========================
# SCHEMAS
# ========================
from modules.vehicles.api.schemas import (
    VehicleResponse,
    VehicleSearchFilters,
    VehicleListResponse
)

# =========================
# DEPENDENCIES
# =========================
from modules.vehicles.api.dependencies import (
    get_vehicle_detail_uc,
    get_get_vehicles_client_uc
)

# =========================
# USE CASES
# =========================
from modules.vehicles.application.use_cases.get_vehicle_detail import GetVehicleDetail
from modules.vehicles.application.use_cases.get_vehicles import GetVehiclesForClientUseCase

# =========================
# AUTH
# =========================
from core.security.dependencies import get_current_user

router = APIRouter(tags=["Vehicles"])

# =========================
# get_vehicle_detail
# =========================
@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_detail(
    vehicle_id: str,
    use_case: GetVehicleDetail = Depends(get_vehicle_detail_uc)
):
    return use_case.execute(vehicle_id)
    
# =========================
# get_vehicles_client
# =========================
@router.get("/", response_model=VehicleListResponse)
def get_vehicles_client(
    filters: VehicleSearchFilters = Depends(),
    use_case: GetVehiclesForClientUseCase = Depends(get_get_vehicles_client_uc),
    current_user=Depends(get_current_user)
):
    return use_case.execute(filters)


    