
from fastapi import Depends

# =========================
# REPOSITORIES
# =========================
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.domain.repositories.vehicle_option_repository import VehicleOptionRepository
from modules.options.domain.repositories.option_repository import OptionRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from modules.leads.domain.repositories.lead_repository import LeadRepository
from modules.quotes.domain.repositories.quote_repository import QuoteRepository
from modules.applications.domain.repositories.application_repository import ApplicationRepository

from modules.dependencies.dependencies import (
    get_option_repository,
    get_vehicle_option_repository,
    get_vehicle_repository,
    get_reservation_repository,
    get_job_queue,
    get_inspection_repository,
    get_reconditioning_repository,
    get_lead_repository,
    get_quote_repository,
    get_application_repository,
    get_vehicle_warranty_repository
)
from modules.storage.api.dependencies import get_s3_service

# =========================
# USE CASES
# =========================
from modules.vehicles.application.use_cases.admin.create_vehicle import CreateVehicle
from modules.vehicles.application.use_cases.admin.update_vehicle import UpdateVehicle
from modules.vehicles.application.use_cases.admin.create_vehicle import AssignOptionsToVehicleUseCase
from modules.vehicles.application.use_cases.admin.final_check import FinalCheckUseCase
from modules.vehicles.application.use_cases.admin.publish_vehicle import PublishVehicleUseCase
from modules.vehicles.application.use_cases.admin.set_availibity import SetAvailabilityUseCase
from modules.vehicles.application.use_cases.admin.delete_vehicle import DeleteVehicle
from modules.vehicles.application.use_cases.get_vehicle_detail import GetVehicleDetailUseCase
from modules.vehicles.application.use_cases.get_vehicles import GetVehiclesForClientUseCase, GetVehiclesForAdminUseCase
from modules.vehicles.application.use_cases.get_vehicle_availability import GetVehicleAvailabilityUseCase
from modules.vehicles.application.use_cases.get_vehicle_interest_status import GetVehicleInterestStatus

# =========================
# SERVICE
# =========================
from modules.storage.infrastrucure.s3_service import S3Service
from modules.applications.api.dependencies import get_event_service

# =========================
# MAPPER
# =========================
from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper

# =========================
# CORE
# =========================
from core.database.unit_of_work import UnitOfWork
from core.database.dependencies import (
    get_unit_of_work
)

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
    event_service=Depends(get_event_service),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return CreateVehicle(
        repo = vehicle_repo,
        assign_options_uc = assign_options_uc,
        event_service=event_service,
        unit_of_work=unit_of_work
)

# =====================================================
# UPDATE VEHICLE
# =====================================================
def get_update_vehicle_use_case(
    vehicle_repo: VehicleRepository = Depends(get_vehicle_repository),
    vehicle_warranty_repository = Depends(get_vehicle_warranty_repository),
    assign_options_uc: AssignOptionsToVehicleUseCase = Depends(get_assign_options_vehicle_uc),
    event_service=Depends(get_event_service),
    unit_of_work=Depends(
        get_unit_of_work
    ),
    s3_service: S3Service = Depends(get_s3_service),
):
    return UpdateVehicle(
        repo = vehicle_repo,
        vehicle_warranty_repository=vehicle_warranty_repository,
        assign_options_uc = assign_options_uc,
        event_service=event_service,
        unit_of_work=unit_of_work,
        s3_service=s3_service

)

# =====================================================
# GET VEHICLE DETAIL
# =====================================================
def get_vehicle_detail_uc(
    vehicle_repository: VehicleRepository = Depends(get_vehicle_repository),

):
    return GetVehicleDetailUseCase(vehicle_repository)

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
    s3_service: S3Service = Depends(get_s3_service),
    event_service=Depends(get_event_service),
    unit_of_work: UnitOfWork = Depends(get_unit_of_work),
):

    return DeleteVehicle(
        repo=repo,
        s3_service=s3_service,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


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
    event_service=Depends(get_event_service),
        unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return FinalCheckUseCase(
        vehicle_repository=vehicle_repository,
        reconditioning_repository=reconditioning_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )

# =====================================================
# PUBLISH VEHICLE
# =====================================================
def get_publish_vehicle_uc(
    vehicle_repository=Depends(get_vehicle_repository),
    event_service=Depends(get_event_service),
    unit_of_work=Depends(
        get_unit_of_work
    )
):
    return PublishVehicleUseCase(
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        unit_of_work=unit_of_work
)

# =====================================================
# TOGGLE AVAIBILITY
# =====================================================
def get_set_availability_uc(
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
    event_service=Depends(get_event_service),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
):

    return SetAvailabilityUseCase(
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        unit_of_work=unit_of_work
    )



# =====================================================
# GET VEHICLE INTEREST STATUS
# =====================================================
def get_vehicle_interest_status_uc(
    lead_repository: LeadRepository = Depends(get_lead_repository),
    quote_repository : QuoteRepository = Depends(get_quote_repository),
    application_repository : ApplicationRepository = Depends(get_application_repository)

):
    return GetVehicleInterestStatus(lead_repository, quote_repository, application_repository)