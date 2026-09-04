from fastapi import APIRouter, Depends

# =========================
# SCHEMAS
# =========================

from modules.vehicles.api.schemas import (
    VehicleResponse,
    VehicleSearchFilters,
    PaginatedVehicleResponse,
    VehicleInterestStatusResponse,
    UnavailableDateResponse,
)

# =========================
# DEPENDENCIES
# =========================

from modules.vehicles.api.dependencies import (
    get_vehicle_detail_usecase,
    get_get_vehicles_client_usecase,
    get_vehicle_availability_usecase,
    get_vehicle_interest_status_usecase,
)
from modules.dependencies.dependencies import (
    get_vehicle_response_mapper,
)
# =========================
# USE CASES
# =========================

from modules.vehicles.application.use_cases.get_vehicle_detail import (
    GetVehicleDetailUseCase,
)

from modules.vehicles.application.use_cases.get_vehicles import (
    GetVehiclesForClientUseCase,
)

from modules.vehicles.application.use_cases.get_vehicle_availability import (
    GetVehicleAvailabilityUseCase,
)

from modules.vehicles.application.use_cases.get_vehicle_interest_status import (
    GetVehicleInterestStatusUseCase,
)

# =========================
# DTOs
# =========================

from modules.vehicles.application.dtos.vehicle_search_filters_dto import (
    VehicleSearchFiltersDTO,
)

# =========================
# MAPPER
# =========================

from modules.vehicles.infrastructure.mappers.vehicle_response_mapper import VehicleResponseMapper

# =========================
# AUTH
# =========================

from core.security.dependencies import get_current_user


router = APIRouter(
    tags=["Vehicles"]
)


# =====================================================
# GET VEHICLE DETAIL
# =====================================================

@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
def get_vehicle_detail(
    vehicle_id: str,
    use_case: GetVehicleDetailUseCase = Depends(
        get_vehicle_detail_usecase
    ),
    response_mapper: VehicleResponseMapper = Depends(
        get_vehicle_response_mapper
    ),
):

    vehicle = use_case.execute(
        vehicle_id
    )

    return response_mapper.to_response(
        vehicle
    )


# =====================================================
# GET VEHICLES CLIENT
# =====================================================

@router.get(
    "",
    response_model=PaginatedVehicleResponse,
)
def get_vehicles(
    query: VehicleSearchFilters = Depends(),

    use_case: GetVehiclesForClientUseCase = Depends(
        get_get_vehicles_client_usecase
    ),
    response_mapper: VehicleResponseMapper = Depends(
        get_vehicle_response_mapper
    ),
):

    # =========================
    # API → APPLICATION DTO
    # =========================

    dto = VehicleSearchFiltersDTO(
        page=query.page,
        size=query.size,

        sort_by=query.sort_by,
        order=query.order,

        search=query.search,

        type=query.type,
        brand=query.brand,
        model=query.model,

        price_min=query.price_min,
        price_max=query.price_max,

        year_min=query.year_min,
        mileage_max=query.mileage_max,

        is_available=query.is_available,

        license_plate=query.license_plate,
    )

    # =========================
    # APPLICATION
    # =========================

    result = use_case.execute(
        dto
    )

    # =========================
    # APPLICATION → API
    # =========================

    return response_mapper.to_paginated_response(
        result
    )


# =====================================================
# GET UNAVAILABLE DATES
# =====================================================

@router.get(
    "/{vehicle_id}/unavailable-dates",
    response_model=list[UnavailableDateResponse],
)
def get_unavailable_dates(
    vehicle_id: str,

    use_case: GetVehicleAvailabilityUseCase = Depends(
        get_vehicle_availability_usecase
    ),
):

    return use_case.execute(
        vehicle_id
    )


# =====================================================
# GET INTEREST STATUS
# =====================================================

@router.get(
    "/{vehicle_id}/interest-status",
    response_model=VehicleInterestStatusResponse,
)
def get_vehicle_interest_status(
    vehicle_id: str,

    current_user=Depends(
        get_current_user
    ),

    use_case: GetVehicleInterestStatusUseCase = Depends(
        get_vehicle_interest_status_usecase
    ),
):

    # =========================
    # APPLICATION
    # =========================

    result = use_case.execute(
        vehicle_id=vehicle_id,
        user_id=current_user.id,
    )

    # =========================
    # APPLICATION → API
    # =========================

    return VehicleResponseMapper.to_interest_status_response(
        result
    )