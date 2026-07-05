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
    get_get_vehicles_client_uc,
    get_vehicle_availability_usecase
)

# =========================
# USE CASES
# =========================
from modules.vehicles.application.use_cases.get_vehicle_detail import GetVehicleDetail
from modules.vehicles.application.use_cases.get_vehicles import GetVehiclesForClientUseCase
from modules.vehicles.application.use_cases.get_vehicle_avaibility import GetVehicleAvailabilityUseCase
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
):
    return use_case.execute(filters)


@router.get(
    "/{vehicle_id}/unavailable-dates"
)
def get_unavailable_dates(
    vehicle_id: str,
    usecase: GetVehicleAvailabilityUseCase = Depends(
        get_vehicle_availability_usecase
    )
):
    return usecase.execute(vehicle_id)
