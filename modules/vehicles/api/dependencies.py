from fastapi import Depends

# =====================================================
# REPOSITORIES
# =====================================================

from modules.vehicles.domain.repositories.vehicle_repository import (
    VehicleRepository,
)

from modules.vehicles.domain.repositories.vehicle_option_repository import (
    VehicleOptionRepository,
)

from modules.options.domain.repositories.option_repository import (
    OptionRepository,
)

from modules.reservations.domain.repositories.reservation_repository import (
    ReservationRepository,
)

from modules.leads.domain.repositories.lead_repository import (
    LeadRepository,
)

from modules.quotes.domain.repositories.quote_repository import (
    QuoteRepository,
)

from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository,
)


# =====================================================
# SHARED DEPENDENCIES
# =====================================================

from modules.dependencies.dependencies import (
    get_option_repository,
    get_vehicle_option_repository,
    get_vehicle_repository,
    get_reservation_repository,
    get_event_service,
    get_inspection_repository,
    get_reconditioning_repository,
    get_lead_repository,
    get_quote_repository,
    get_application_repository,
    get_vehicle_warranty_repository,
)


# =====================================================
# STORAGE
# =====================================================

from modules.storage.api.dependencies import (
    get_s3_service,
)

from modules.storage.infrastrucure.s3_service import (
    S3Service,
)


# =====================================================
# CORE
# =====================================================

from core.database.unit_of_work import UnitOfWork
from core.database.dependencies import (
    get_unit_of_work,
)


# =====================================================
# USE CASES
# =====================================================

# ADMIN

from modules.vehicles.application.use_cases.admin.create_vehicle import (
    CreateVehicleUseCase,
    AssignOptionsToVehicleUseCase,
)

from modules.vehicles.application.use_cases.admin.update_vehicle import (
    UpdateVehicleUseCase,
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


# CLIENT / SHARED

from modules.vehicles.application.use_cases.get_vehicle_detail import (
    GetVehicleDetailUseCase,
)

from modules.vehicles.application.use_cases.get_vehicles import (
    GetVehiclesForClientUseCase,
    GetVehiclesForAdminUseCase,
)

from modules.vehicles.application.use_cases.get_vehicle_availability import (
    GetVehicleAvailabilityUseCase,
)

from modules.vehicles.application.use_cases.get_vehicle_interest_status import (
    GetVehicleInterestStatusUseCase,
)


# =====================================================
# ADMIN - ASSIGN OPTIONS
# =====================================================

def get_assign_options_vehicle_usecase(
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
    option_repository: OptionRepository = Depends(
        get_option_repository
    ),
    vehicle_option_repository: VehicleOptionRepository = Depends(
        get_vehicle_option_repository
    ),
):
    return AssignOptionsToVehicleUseCase(
        vehicle_repository=vehicle_repository,
        option_repository=option_repository,
        vehicle_option_repository=vehicle_option_repository,
    )


# =====================================================
# ADMIN - CREATE VEHICLE
# =====================================================

def get_create_vehicle_usecase(
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
    warranty_repository=Depends(
        get_vehicle_warranty_repository
    ),
    assign_options_uc: AssignOptionsToVehicleUseCase = Depends(
        get_assign_options_vehicle_usecase
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
):
    return CreateVehicleUseCase(
        vehicle_repository=vehicle_repository,
        warranty_repository=warranty_repository,
        assign_options_usecase=assign_options_uc,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# =====================================================
# ADMIN - GET VEHICLES
# =====================================================

def get_get_vehicles_admin_usecase(
    repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
):
    return GetVehiclesForAdminUseCase(
        repository
    )


# =====================================================
# ADMIN - DELETE VEHICLE
# =====================================================

def get_delete_vehicle_usecase(
    repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
    s3_service: S3Service = Depends(
        get_s3_service
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
):
    return DeleteVehicleUseCase(
        repository=repository,
        s3_service=s3_service,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# =====================================================
# ADMIN - FINAL CHECK
# =====================================================

def get_final_check_usecase(
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
    reconditioning_repository=Depends(
        get_reconditioning_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work: UnitOfWork = Depends(
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
# ADMIN - GET VEHICLE LIFECYCLE
# =====================================================

def get_vehicle_lifecycle_usecase(
    inspection_repository=Depends(
        get_inspection_repository
    ),
    reconditioning_repository=Depends(
        get_reconditioning_repository
    ),
):
    return GetVehicleLifecycleUseCase(
        inspection_repository=inspection_repository,
        reconditioning_repository=reconditioning_repository,
    )


# =====================================================
# ADMIN - PUBLISH VEHICLE
# =====================================================

def get_publish_vehicle_usecase(
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
):
    return PublishVehicleUseCase(
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# =====================================================
# ADMIN - SET AVAILABILITY
# =====================================================

def get_set_availability_usecase(
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
):
    return SetAvailabilityUseCase(
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# =====================================================
# ADMIN - UPDATE VEHICLE
# =====================================================

def get_update_vehicle_usecase(
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
    vehicle_warranty_repository=Depends(
        get_vehicle_warranty_repository
    ),
    assign_options_uc: AssignOptionsToVehicleUseCase = Depends(
        get_assign_options_vehicle_usecase
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work: UnitOfWork = Depends(
        get_unit_of_work
    ),
    s3_service: S3Service = Depends(
        get_s3_service
    ),
):
    return UpdateVehicleUseCase(
        repo=vehicle_repository,
        vehicle_warranty_repository=vehicle_warranty_repository,
        assign_options_uc=assign_options_uc,
        event_service=event_service,
        unit_of_work=unit_of_work,
        s3_service=s3_service,
    )


# =====================================================
# SHARED - GET VEHICLE DETAIL
# =====================================================

def get_vehicle_detail_usecase(
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
):
    return GetVehicleDetailUseCase(
        vehicle_repository
    )


# =====================================================
# CLIENT - GET VEHICLE AVAILABILITY
# =====================================================

def get_vehicle_availability_usecase(
    reservation_repository: ReservationRepository = Depends(
        get_reservation_repository
    ),
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
):
    return GetVehicleAvailabilityUseCase(
        reservation_repository=reservation_repository,
        vehicle_repository=vehicle_repository,
    )


# =====================================================
# CLIENT - GET VEHICLE INTEREST STATUS
# =====================================================

def get_vehicle_interest_status_usecase(
    lead_repository: LeadRepository = Depends(
        get_lead_repository
    ),
    quote_repository: QuoteRepository = Depends(
        get_quote_repository
    ),
    application_repository: ApplicationRepository = Depends(
        get_application_repository
    ),
):
    return GetVehicleInterestStatusUseCase(
        lead_repository=lead_repository,
        quote_repository=quote_repository,
        application_repository=application_repository,
    )


# =====================================================
# CLIENT - GET VEHICLES
# =====================================================

def get_get_vehicles_client_usecase(
    repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
):
    return GetVehiclesForClientUseCase(
        repository
    )