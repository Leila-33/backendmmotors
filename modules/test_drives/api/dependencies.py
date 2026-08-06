from fastapi import Depends

# =========================
# DEPENDENCIES
# =========================
from modules.dependencies.dependencies import (
    get_test_drive_repository,
    get_event_repository,
    get_vehicle_repository
)
# =========================
# SERVICE
# =========================
from modules.notifications.api.dependencies import (
    get_notification_service,
)
from modules.applications.api.dependencies import get_event_service

# =========================
# CORE
# =========================
from core.database.unit_of_work import UnitOfWork
from core.database.dependencies import (
    get_unit_of_work
)

# =========================
# REPOSITORIES
# =========================
from modules.test_drives.domain.repositories.test_drive_repository import (
    TestDriveRepository,
)
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository

# =========================
# CLIENT USE CASES
# =========================

from modules.test_drives.application.use_cases.create_test_drive import (
    CreateTestDriveUseCase,
)

from modules.test_drives.application.use_cases.get_avaibility import (
    GetAvailabilityUseCase,
)

from modules.test_drives.application.use_cases.get_my_test_drives import (
    GetMyTestDrivesUseCase,
)

from modules.test_drives.application.use_cases.get_test_drive_details_client import (
    GetTestDriveDetailClientUseCase,
)


def get_create_test_drive_usecase(
    test_drive_repository=Depends(get_test_drive_repository),
    vehicle_repository=Depends(get_vehicle_repository),
    event_service=Depends(get_event_service),
        unit_of_work=Depends(
        get_unit_of_work
    ),):
    return CreateTestDriveUseCase(
        test_drive_repository=test_drive_repository,
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        unit_of_work=unit_of_work
    )


def get_availability_usecase(
    repository: TestDriveRepository = Depends(
        get_test_drive_repository
    ),
    vehicle_repository: VehicleRepository = Depends(get_vehicle_repository) 
):
    return GetAvailabilityUseCase(
        repository=repository,
        vehicle_repository=vehicle_repository
    )


def get_my_test_drives_usecase(
    repository=Depends(get_test_drive_repository),
):
    return GetMyTestDrivesUseCase(
        repository=repository
    )


def get_test_drive_detail_client_usecase(
    repository=Depends(get_test_drive_repository),
    event_repository=Depends(get_event_repository),
):
    return GetTestDriveDetailClientUseCase(
        repository=repository,
        event_repository=event_repository,
    )


# =========================
# ADMIN USE CASES
# =========================

from modules.test_drives.application.use_cases.admin.get_test_drives import (
    GetTestDrivesAdminUseCase,
)

from modules.test_drives.application.use_cases.admin.get_test_drive_details import (
    GetTestDriveDetailsUseCase,
)

from modules.test_drives.application.use_cases.admin.update_test_drive_status import (
    UpdateTestDriveStatusUseCase,
)

from modules.test_drives.application.use_cases.admin.get_pending_count_test_drive import GetPendingTestDriveCountUseCase

def get_test_drives_admin_usecase(
    repository=Depends(get_test_drive_repository),
):
    return GetTestDrivesAdminUseCase(
        repository=repository
    )


def get_test_drive_detail_usecase(
    repository=Depends(get_test_drive_repository),
):
    return GetTestDriveDetailsUseCase(
        repository=repository
    )


def get_update_test_drive_status_usecase(
    repository=Depends(get_test_drive_repository),
    notification_service=Depends(get_notification_service),
    event_service=Depends(get_event_service),
    unit_of_work=Depends(
        get_unit_of_work
    )
):
    return UpdateTestDriveStatusUseCase(
        repository=repository,
        notification_service=notification_service,
        event_service=event_service,
        unit_of_work=unit_of_work
    )

def get_pending_test_drive_count_usecase(
    repo=Depends(get_test_drive_repository)
):

    return GetPendingTestDriveCountUseCase(
        repository=repo
    )