from fastapi import Depends

# =========================
# DEPENDENCIES
# =========================

from modules.dependencies.dependencies import (
    get_test_drive_repository,
    get_event_repository,
    get_vehicle_repository,
    get_event_service,
    get_user_repository,
    get_websocket_manager
)

# =========================
# SERVICES
# =========================

from modules.notifications.api.dependencies import (
    get_notification_service,
)

# =========================
# CORE
# =========================

from core.database.dependencies import (
    get_unit_of_work,
)

# =========================
# REPOSITORIES
# =========================

from modules.test_drives.domain.repositories.test_drive_repository import (
    TestDriveRepository,
)

from modules.vehicles.domain.repositories.vehicle_repository import (
    VehicleRepository,
)

# =========================
# CLIENT USE CASES
# =========================

from modules.test_drives.application.use_cases.create_test_drive import (
    CreateTestDriveUseCase,
)

from modules.test_drives.application.use_cases.get_availability import (
    GetAvailabilityUseCase,
)

from modules.test_drives.application.use_cases.get_my_test_drives import (
    GetMyTestDrivesUseCase,
)

# =========================
# SHARED USE CASES
# =========================

from modules.test_drives.application.use_cases.get_test_drive_detail import (
    GetTestDriveDetailUseCase,
)

from modules.test_drives.application.use_cases.update_test_drive_status import (
    UpdateTestDriveStatusUseCase,
)

# =========================
# ADMIN USE CASES
# =========================

from modules.test_drives.application.use_cases.admin.get_test_drives_admin import (
    GetTestDrivesAdminUseCase,
)

from modules.test_drives.application.use_cases.admin.get_pending_test_drive_count import (
    GetPendingTestDriveCountUseCase,
)


# =========================================================
# CLIENT
# =========================================================

def get_create_test_drive_usecase(
    user_repository=Depends(get_user_repository),
    test_drive_repository=Depends(
        get_test_drive_repository
    ),
    vehicle_repository=Depends(
        get_vehicle_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    notification_service=Depends(get_notification_service),
    unit_of_work=Depends(
        get_unit_of_work
    ),
    websocket_manager=Depends(get_websocket_manager),

):
    return CreateTestDriveUseCase(
        user_repository=user_repository,
        test_drive_repository=test_drive_repository,
        vehicle_repository=vehicle_repository,
        event_service=event_service,
        notification_service=notification_service,
        unit_of_work=unit_of_work,
        websocket_manager=websocket_manager,
    )


def get_get_availability_usecase(
    repository: TestDriveRepository = Depends(
        get_test_drive_repository
    ),
    vehicle_repository: VehicleRepository = Depends(
        get_vehicle_repository
    ),
):
    return GetAvailabilityUseCase(
        repository=repository,
        vehicle_repository=vehicle_repository,
    )


def get_my_test_drives_usecase(
    repository=Depends(
        get_test_drive_repository
    ),
):
    return GetMyTestDrivesUseCase(
        repository=repository,
    )


# =========================================================
# SHARED — DETAIL
# =========================================================

def get_get_test_drive_detail_usecase(
    repository=Depends(
        get_test_drive_repository
    ),
    event_repository=Depends(
        get_event_repository
    ),
):
    return GetTestDriveDetailUseCase(
        repository=repository,
        event_repository=event_repository,
    )


# =========================================================
# SHARED — STATUS
# =========================================================

def get_update_test_drive_status_usecase(
    repository=Depends(
        get_test_drive_repository
    ),
    user_repository=Depends(get_user_repository),
    notification_service=Depends(
        get_notification_service
    ),
    event_service=Depends(
        get_event_service
    ),
    websocket_manager=Depends(get_websocket_manager),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):
    return UpdateTestDriveStatusUseCase(
        repository=repository,
        user_repository=user_repository,
        notification_service=notification_service,
        event_service=event_service,
        websocket_manager=websocket_manager,
        unit_of_work=unit_of_work,
    )


# =========================================================
# ADMIN
# =========================================================

def get_pending_test_drive_count_usecase(
    repository=Depends(
        get_test_drive_repository
    ),
):
    return GetPendingTestDriveCountUseCase(
        repository=repository,
    )


def get_get_test_drives_admin_usecase(
    repository=Depends(
        get_test_drive_repository
    ),
):
    return GetTestDrivesAdminUseCase(
        repository=repository,
    )