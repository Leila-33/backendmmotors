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
SetAvailabilityRequest,
DeleteVehicleResponse
)

# =========================
# DEPENDENCIES (REPOSITORIES)
# =========================
from modules.vehicles.api.dependencies import(
    get_create_vehicle_use_case,
    get_update_vehicle_use_case,
    get_get_vehicles_admin_uc,
    get_delete_vehicle_use_case,
    get_vehicle_lifecycle_uc,
    get_final_check_uc,
    get_publish_vehicle_uc,
    get_set_availability_uc
) 
from modules.dependencies.dependencies import get_vehicle_response_mapper
# =========================
# USE CASES
# =========================
from modules.vehicles.application.use_cases.admin.create_vehicle import CreateVehicle
from modules.vehicles.application.use_cases.admin.update_vehicle import UpdateVehicle
from modules.vehicles.application.use_cases.get_vehicles import GetVehiclesForAdminUseCase
from modules.vehicles.application.use_cases.admin.delete_vehicle import DeleteVehicle
from modules.vehicles.application.use_cases.admin.final_check import FinalCheckUseCase
from modules.vehicles.application.use_cases.admin.publish_vehicle import PublishVehicleUseCase
from modules.vehicles.application.use_cases.admin.set_availibity import SetAvailabilityUseCase
from modules.vehicles.application.use_cases.admin.get_vehicle_lifecycle import GetVehicleLifecycleUseCase


# =========================
# MAPPER
# =========================
from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper

router = APIRouter(tags=["Admin Vehicles"])


# =========================
# ROUTE
# =========================
@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
    payload: CreateVehicleRequest,
    current_admin=Depends(get_current_admin),
    use_case: CreateVehicleUseCase = Depends(
        get_create_vehicle_usecase
    ),
):

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

    vehicle = use_case.execute(
        dto=dto,
        admin_id=current_admin.id,
    )

    return VehicleMapper.to_response(vehicle)

# =====================================================
#  UPDATE VEHICLE
# =====================================================
@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: str,
    data: UpdateVehicleRequest,
    use_case: UpdateVehicle = Depends(get_update_vehicle_use_case),
    mapper: VehicleMapper = Depends(get_vehicle_response_mapper),
    current_admin=Depends(get_current_admin)
):
    vehicle = use_case.execute(
        vehicle_id=vehicle_id,
        data=data
    )
    return mapper.to_response(vehicle, current_admin)


# =========================
# GET VEHICLES ADMIN
# =========================
@router.get("/", response_model=VehicleListResponse)
def get_vehicles_admin(
    filters: VehicleSearchFilters = Depends(),
    use_case: GetVehiclesForAdminUseCase = Depends(get_get_vehicles_admin_uc),
    mapper: VehicleMapper = Depends(get_vehicle_response_mapper),
    admin=Depends(get_current_admin)
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
# DELETE VEHICLE
# =========================
@router.delete("/{vehicle_id}", response_model=DeleteVehicleResponse)
def delete_vehicle(
    vehicle_id: str,
    use_case: DeleteVehicle = Depends(get_delete_vehicle_use_case),
    current_admin=Depends(get_current_admin)
):
    return use_case.execute(vehicle_id, current_admin)






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

    return uc.execute(vehicle_id, current_admin)

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



# =========================
# SET AVAILABILIY
# =========================
@router.patch(
    "/{vehicle_id}/availability",
    response_model=VehicleResponse
)
def set_availability(
    vehicle_id: str,
    request: SetAvailabilityRequest,
    use_case: SetAvailabilityUseCase = Depends(
        get_set_availability_uc
    ),
    mapper: VehicleMapper = Depends(get_vehicle_response_mapper),
    current_admin=Depends(get_current_admin)
):

    vehicle = use_case.execute(
        vehicle_id,
        request.value,
        current_admin
    )

    return mapper.to_response(vehicle, current_admin)