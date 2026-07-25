from fastapi import Depends

from modules.dependencies.dependencies import (
    get_test_drive_repository,
    get_event_repository,
)

from modules.notifications.api.dependencies import (
    get_notification_service,
)

from modules.test_drives.domain.repositories.test_drive_repository import (
    TestDriveRepository,
)

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
    repository=Depends(get_test_drive_repository),
):
    return CreateTestDriveUseCase(
        repository=repository
    )


def get_availability_usecase(
    repository: TestDriveRepository = Depends(
        get_test_drive_repository
    ),
):
    return GetAvailabilityUseCase(
        repository=repository
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


def get_test_drive_admin_usecase(
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
    event_repository=Depends(get_event_repository),
):
    return UpdateTestDriveStatusUseCase(
        repository=repository,
        notification_service=notification_service,
        event_repository=event_repository,
    )