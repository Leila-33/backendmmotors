from fastapi import APIRouter, Depends, status

# =====================================================
# AUTH
# =====================================================

from core.security.dependencies import get_current_admin


# =====================================================
# SCHEMAS
# =====================================================

from modules.vehicles.api.schemas import (
    CreateVehicleRequest,
    VehicleResponse,
    UpdateVehicleRequest,
    VehicleSearchFilters,
    PaginatedVehicleResponse,
    VehicleLifecycleResponse,
    SetAvailabilityRequest,
    DeleteVehicleResponse,
    FinalCheckResponse,
    VehicleActionResponse,
)


# =====================================================
# DTOs
# =====================================================

from modules.vehicles.application.dtos.admin.create_vehicle_dto import (
    CreateVehicleDTO,
)

from modules.vehicles.application.dtos.admin.update_vehicle_dto import (
    UpdateVehicleDTO,
)

from modules.vehicles.application.dtos.vehicle_search_filters_dto import (
    VehicleSearchFiltersDTO,
)

from modules.vehicles.application.dtos.admin.vehicle_admin_action_dto import (
    VehicleAdminActionDTO,
)  
from modules.vehicles.application.dtos.admin.set_availability_dto import (
    SetAvailabilityDTO,
)


# =====================================================
# DEPENDENCIES
# =====================================================

from modules.vehicles.api.dependencies import (
    get_create_vehicle_usecase,
    get_update_vehicle_usecase,
    get_get_vehicles_admin_usecase,
    get_delete_vehicle_usecase,
    get_vehicle_lifecycle_usecase,
    get_final_check_usecase,
    get_publish_vehicle_usecase,
    get_set_availability_usecase,
)

from modules.dependencies.dependencies import (
    get_vehicle_response_mapper,
)
# =====================================================
# USE CASES
# =====================================================

from modules.vehicles.application.use_cases.admin.create_vehicle import (
    CreateVehicleUseCase,
)

from modules.vehicles.application.use_cases.admin.update_vehicle import (
    UpdateVehicleUseCase,
)

from modules.vehicles.application.use_cases.get_vehicles import (
    GetVehiclesForAdminUseCase,
)

from modules.vehicles.application.use_cases.admin.delete_vehicle import (
    DeleteVehicleUseCase,
)

from modules.vehicles.application.use_cases.admin.final_check import (
    FinalCheckUseCase,
)

from modules.vehicles.application.use_cases.admin.publish_vehicle import (
    PublishVehicleUseCase,
)

from modules.vehicles.application.use_cases.admin.set_availability import (
    SetAvailabilityUseCase,
)

from modules.vehicles.application.use_cases.admin.get_vehicle_lifecycle import (
    GetVehicleLifecycleUseCase,
)


# =====================================================
# MAPPERS
# =====================================================

from modules.vehicles.infrastructure.mappers.vehicle_response_mapper import (
    VehicleResponseMapper,
)





# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    tags=["Admin Vehicles"]
)


# =====================================================
# CREATE VEHICLE
# =====================================================

@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
    payload: CreateVehicleRequest,

    current_admin=Depends(
        get_current_admin
    ),

    use_case: CreateVehicleUseCase = Depends(
        get_create_vehicle_usecase
    ),

    response_mapper: VehicleResponseMapper = Depends(
        get_vehicle_response_mapper
    ),
):

    # =========================
    # API → APPLICATION DTO
    # =========================

    dto = CreateVehicleDTO(
        brand=payload.brand,
        model=payload.model,
        price=payload.price,
        type=payload.type,
        mileage=payload.mileage,
        year=payload.year,
        description=payload.description,
        engine_type=payload.engine_type,
        equipments=payload.equipments,
        condition=payload.condition,
        images=payload.images,
        license_plate=payload.license_plate,
        warranty_plan_id=payload.warranty_plan_id,
        included_options=payload.included_options,
        optional_options=payload.optional_options,
    )

    # =========================
    # APPLICATION
    # =========================

    result = use_case.execute(
        dto=dto,
        admin_id=current_admin.id,
    )

    # =========================
    # APPLICATION → API
    # =========================

    return response_mapper.to_response(
        result
    )


# =====================================================
# UPDATE VEHICLE
# =====================================================

@router.put(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
def update_vehicle(
    vehicle_id: str,

    request: UpdateVehicleRequest,

    current_admin=Depends(
        get_current_admin
    ),

    use_case: UpdateVehicleUseCase = Depends(
        get_update_vehicle_usecase
    ),

    response_mapper: VehicleResponseMapper = Depends(
        get_vehicle_response_mapper
    ),
):

    # =========================
    # API → APPLICATION DTO
    # =========================

    dto = UpdateVehicleDTO(
        vehicle_id=vehicle_id,
        admin_id=current_admin.id,
        **request.model_dump(),
    )

    # =========================
    # APPLICATION
    # =========================

    vehicle = use_case.execute(dto)

    # =========================
    # APPLICATION → API
    # =========================

    return response_mapper.to_response(
        vehicle
    )


# =====================================================
# GET VEHICLES ADMIN
# =====================================================

@router.get(
    "",
    response_model=PaginatedVehicleResponse,
)
def get_vehicles_admin(
    query: VehicleSearchFilters = Depends(),

    current_admin=Depends(
        get_current_admin
    ),

    use_case: GetVehiclesForAdminUseCase = Depends(
        get_get_vehicles_admin_usecase
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

    result = use_case.execute(dto)

    # =========================
    # APPLICATION → API
    # =========================

    return response_mapper.to_paginated_response(
        result
    )


# =====================================================
# DELETE VEHICLE
# =====================================================

@router.delete(
    "/{vehicle_id}",
    response_model=DeleteVehicleResponse,
)
def delete_vehicle(
    vehicle_id: str,

    current_admin=Depends(
        get_current_admin
    ),

    use_case: DeleteVehicleUseCase = Depends(
        get_delete_vehicle_usecase
    ),
):

    # =========================
    # API → APPLICATION DTO
    # =========================

    dto = VehicleAdminActionDTO(
        vehicle_id=vehicle_id,
        admin_id=current_admin.id,
    )

    # =========================
    # APPLICATION
    # =========================

    result = use_case.execute(dto)

    # =========================
    # RESPONSE
    # =========================

    message = (
        "Véhicule archivé"
        if result.action == "ARCHIVED"
        else "Véhicule supprimé définitivement"
    )

    return DeleteVehicleResponse(
        vehicle_id=result.vehicle_id,
        action=result.action,
        message=message,
    )


# =====================================================
# GET VEHICLE LIFECYCLE
# =====================================================

@router.get(
    "/{vehicle_id}/lifecycle",
    response_model=VehicleLifecycleResponse,
)
def get_vehicle_lifecycle(
    vehicle_id: str,

    current_admin=Depends(
        get_current_admin
    ),

    use_case: GetVehicleLifecycleUseCase = Depends(
        get_vehicle_lifecycle_usecase
    ),
):

    result = use_case.execute(
        vehicle_id=vehicle_id
    )

    return VehicleResponseMapper.to_lifecycle_response(
        result
    )


# =====================================================
# FINAL CHECK
# =====================================================

@router.post(
    "/{vehicle_id}/final-check",
    response_model=FinalCheckResponse,
)
def final_check(
    vehicle_id: str,

    current_admin=Depends(
        get_current_admin
    ),

    use_case: FinalCheckUseCase = Depends(
        get_final_check_usecase
    ),
):

    dto = VehicleAdminActionDTO(
    vehicle_id=vehicle_id,
    admin_id=current_admin.id,
)

    result = use_case.execute(
        dto
    )

    return FinalCheckResponse(
        vehicle_id=result.vehicle_id,
        vehicle_status=result.vehicle_status,
        reconditioning_status=result.reconditioning_status,
        final_check_at=result.final_check_at,
    )


# =====================================================
# PUBLISH VEHICLE
# =====================================================

@router.post(
    "/{vehicle_id}/publish",
    response_model=VehicleActionResponse,
)
def publish_vehicle(
    vehicle_id: str,

    current_admin=Depends(
        get_current_admin
    ),

    use_case: PublishVehicleUseCase = Depends(
        get_publish_vehicle_usecase
    ),
):

    dto = VehicleAdminActionDTO(
    vehicle_id=vehicle_id,
    admin_id=current_admin.id,
)

    result = use_case.execute(
        dto
    )

    return VehicleActionResponse(
        vehicle_id=result.vehicle_id,
        status=result.status,
        message=result.message,
    )


# =====================================================
# SET AVAILABILITY
# =====================================================

@router.patch(
    "/{vehicle_id}/availability",
    response_model=VehicleActionResponse,
)
def set_vehicle_availability(
    vehicle_id: str,

    data: SetAvailabilityRequest,

    current_admin=Depends(
        get_current_admin
    ),

    use_case: SetAvailabilityUseCase = Depends(
        get_set_availability_usecase
    ),
):

    dto = SetAvailabilityDTO(
        vehicle_id=vehicle_id,
        value=data.value,
        admin_id=current_admin.id,
    )

    result = use_case.execute(
        dto
    )

    return VehicleActionResponse(
        vehicle_id=result.vehicle_id,
        status=result.status,
        message=result.message,
    )