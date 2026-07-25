from fastapi import APIRouter, Depends

# =========================
# SCHEMAS
# ========================
from modules.vehicles.api.schemas import (
    VehicleResponse,
    VehicleSearchFilters,
    VehicleListResponse,
    VehicleInterestStatusResponse,
    UnavailableDateResponse
)

# =========================
# DEPENDENCIES
# =========================
from modules.vehicles.api.dependencies import (
    get_vehicle_detail_uc,
    get_get_vehicles_client_uc,
    get_vehicle_availability_usecase,
    get_vehicle_interest_status_uc
)

# =========================
# USE CASES
# =========================
from modules.vehicles.application.use_cases.get_vehicle_detail import GetVehicleDetailUseCase
from modules.vehicles.application.use_cases.get_vehicles import GetVehiclesForClientUseCase
from modules.vehicles.application.use_cases.get_vehicle_availability import GetVehicleAvailabilityUseCase
from modules.vehicles.application.use_cases.get_vehicle_interest_status import GetVehicleInterestStatus

# =========================
# MAPPER
# =========================
from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper
from modules.dependencies.dependencies import get_vehicle_response_mapper

# =========================
# AUTH
# =========================
from core.security.dependencies import get_current_user
from modules.auth.infrastructure.db.user_model import UserModel

router = APIRouter(tags=["Vehicles"])

# =========================
# get_vehicle_detail
# =========================
@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_detail(
    vehicle_id: str,
    mapper: VehicleMapper = Depends(get_vehicle_response_mapper),
    use_case: GetVehicleDetailUseCase = Depends(get_vehicle_detail_uc),
):
    vehicle = use_case.execute(vehicle_id)

    return mapper.to_response(vehicle)
    
# =========================
# get_vehicles_client
# =========================
@router.get("/", response_model=VehicleListResponse)
def get_vehicles_client(
    filters: VehicleSearchFilters = Depends(),
    mapper: VehicleMapper = Depends(get_vehicle_response_mapper),
    use_case: GetVehiclesForClientUseCase = Depends(get_get_vehicles_client_uc),
):
    result = use_case.execute(filters)

    return {
        "items": [
            mapper.to_response(v)
            for v in result["items"]
        ],
        "total": result["total"],
        "page": result["page"],
        "size": result["size"]
    }

# =========================
# get_unavaibles_dates
# =========================
@router.get(
    "/{vehicle_id}/unavailable-dates",
    response_model=list[UnavailableDateResponse]
)
def get_unavailable_dates(
    vehicle_id: str,
    usecase: GetVehicleAvailabilityUseCase = Depends(
        get_vehicle_availability_usecase
    )
):

    return usecase.execute(vehicle_id)

# =========================
# get_interest_status
# =========================
@router.get(
    "/{vehicle_id}/interest-status",
    response_model=VehicleInterestStatusResponse
)
def get_interest_status(
    vehicle_id: str,
    current_user: UserModel = Depends(get_current_user),
    use_case: GetVehicleInterestStatus = Depends(
        get_vehicle_interest_status_uc
    )
):

    return use_case.execute(
        vehicle_id,
        current_user.id
    )