
from fastapi import Depends

# =========================
# REPOSITORIES
# =========================
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.domain.repositories.vehicle_option_repository import VehicleOptionRepository
from modules.options.domain.repositories.option_repository import OptionRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository

from modules.core.infrastructure.dependencies import (
    get_option_repository,
    get_vehicle_option_repository,
    get_vehicle_repository,
    get_reservation_repository,
    get_job_queue,
    get_inspection_repository,
    get_reconditioning_repository
)
# =========================
# USE CASES
# =========================
from modules.vehicles.application.use_cases.admin.create_vehicle import CreateVehicle
from modules.vehicles.application.use_cases.admin.update_vehicle import UpdateVehicle
from modules.vehicles.application.use_cases.admin.toggle_vehicle_type import ToggleVehicleType
from modules.vehicles.application.use_cases.admin.create_vehicle import AssignOptionsToVehicleUseCase
from modules.vehicles.application.use_cases.admin.final_check import FinalCheckUseCase
from modules.vehicles.application.use_cases.admin.publish_vehicle import PublishVehicleUseCase
from modules.vehicles.application.use_cases.admin.set_availibity import SetAvailabilityUseCase
from modules.vehicles.application.use_cases.admin.delete_vehicle import DeleteVehicle
from modules.vehicles.application.use_cases.get_vehicle_detail import GetVehicleDetail
from modules.vehicles.application.use_cases.get_vehicles import GetVehiclesForClientUseCase, GetVehiclesForAdminUseCase
from modules.vehicles.application.use_cases.get_vehicle_avaibility import GetVehicleAvailabilityUseCase



# =====================================================
# CREATE VEHICLE
# =====================================================
def get_assign_options_vehicle_uc(
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repository),
    option_repo: OptionRepository = Depends(get_option_repository),
    vehicle_option_repo: VehicleOptionRepository = Depends(get_vehicle_option_repository),
):
    return AssignOptionsToVehicleUseCase(
        vehicle_repo,
        option_repo,
        vehicle_option_repo
    )

def get_create_vehicle_use_case(
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repository),
    assign_options_uc: AssignOptionsToVehicleUseCase = Depends(get_assign_options_vehicle_uc),
):
    return CreateVehicle(vehicle_repo, assign_options_uc)

# =====================================================
# UPDATE VEHICLE
# =====================================================
def get_update_vehicle_use_case(
    repo: VehicleRepository = Depends(get_vehicle_repository),
    assign_options_uc: AssignOptionsToVehicleUseCase = Depends(get_assign_options_vehicle_uc),
):
    return UpdateVehicle(repo, assign_options_uc)

# =====================================================
# TOGGLE TYPE (achat ↔ location)
# =====================================================
def get_toggle_vehicle_type_uc(
    repo: VehicleRepository = Depends(get_vehicle_repository),
):
    return ToggleVehicleType(repo)

# =====================================================
# GET VEHICLE DETAIL
# =====================================================
def get_vehicle_detail_uc(
    vehicle_repository: VehicleRepository = Depends(get_vehicle_repository),
):
    return GetVehicleDetail(vehicle_repository)

# =====================================================
# GET VEHICLES
# =====================================================
def get_get_vehicles_client_uc(
    repo=Depends(get_vehicle_repository)
):
    return GetVehiclesForClientUseCase(repo)


def get_get_vehicles_admin_uc(
    repo=Depends(get_vehicle_repository)
):
    return GetVehiclesForAdminUseCase(repo)

# =====================================================
# DELETE VEHICLE
# =====================================================
def get_delete_vehicle_use_case(
    repo: VehicleRepository = Depends(get_vehicle_repository),
) -> DeleteVehicle:
    return DeleteVehicle(repo)


# =====================================================
# GET AVAIBILITY
# =====================================================
def get_vehicle_availability_usecase(
    reservation_repository: ReservationRepository = Depends(
        get_reservation_repository
    )
) -> GetVehicleAvailabilityUseCase:

    return GetVehicleAvailabilityUseCase(
        reservation_repository=reservation_repository
    )



# =====================================================
# GET LIFECYCLE
# =====================================================
from modules.vehicles.application.use_cases.admin.get_vehicle_lifecycle import GetVehicleLifecycleUseCase

def get_vehicle_lifecycle_uc(
    inspection_repository=Depends(
        get_inspection_repository
    ),
    reconditioning_repository=Depends(
        get_reconditioning_repository
    )
):
    return GetVehicleLifecycleUseCase(
        inspection_repository,
        reconditioning_repository
    )



# =====================================================
# FINAL CHECK
# =====================================================

def get_final_check_uc(
    vehicle_repository=Depends(get_vehicle_repository),
    reconditioning_repository=Depends(get_reconditioning_repository),
):
    return FinalCheckUseCase(
        vehicle_repository,
        reconditioning_repository,
    )

# =====================================================
# PUBLISH VEHICLE
# =====================================================
def get_publish_vehicle_uc(
    vehicle_repository=Depends(get_vehicle_repository),
):
    return PublishVehicleUseCase(vehicle_repository)

# =====================================================
# TOGGLE AVAIBILITY
# =====================================================
def get_set_availability_uc(
    vehicle_repository=Depends(get_vehicle_repository),
):
    return SetAvailabilityUseCase(vehicle_repository)