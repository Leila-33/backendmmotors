
from fastapi import Depends
from infrastructure.db.dependencies import get_db
from sqlalchemy.orm import Session

# =========================
# REPOSITORIES
# =========================
from modules.options.api.dependencies import get_option_repository
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL
from modules.vehicles.infrastructure.repositories.vehicle_option_repository_sql import VehicleOptionRepositorySQL
from modules.vehicles.domain.repositories.vehicle_option_repository import VehicleOptionRepository
from modules.options.domain.repositories.option_repository import OptionRepository

def get_vehicle_repository(db: Session = Depends(get_db)):
    return VehicleRepositorySQL(db)


def get_vehicle_option_repository(db: Session = Depends(get_db)):
    return VehicleOptionRepositorySQL(db)

# =========================
# USE CASES
# =========================
from modules.vehicles.application.use_cases.admin.create_vehicle import CreateVehicle
from modules.vehicles.application.use_cases.admin.update_vehicle import UpdateVehicle
from modules.vehicles.application.use_cases.admin.toggle_vehicle_type import ToggleVehicleType
from modules.vehicles.application.use_cases.admin.create_vehicle import AssignOptionsToVehicleUseCase
from modules.vehicles.application.use_cases.get_vehicle_detail import GetVehicleDetail
from modules.vehicles.application.use_cases.get_vehicles import GetVehiclesForClientUseCase, GetVehiclesForAdminUseCase
from modules.vehicles.application.use_cases.admin.delete_vehicle import DeleteVehicle


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