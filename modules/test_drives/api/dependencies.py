from fastapi import Depends
from infrastructure.db.dependencies import get_db

from modules.test_drives.infrastructure.repositories.test_drive_repository_sql import TestDriveRepositorySQL
from modules.test_drives.application.use_cases.create_test_drive import CreateTestDriveUseCase
from modules.test_drives.domain.repositories.test_drive_repository import TestDriveRepository
from modules.test_drives.application.use_cases.get_avaibility import GetAvailabilityUseCase

def get_test_drive_repository(
    db=Depends(get_db)
):
    return TestDriveRepositorySQL(db)


def get_create_test_drive_usecase(

    repository=Depends(
        get_test_drive_repository
    )
):
    return CreateTestDriveUseCase(
        repository
    )


def get_availability_usecase(
    repository: TestDriveRepository = Depends(
        get_test_drive_repository
    )
):
    return GetAvailabilityUseCase(repository)




from modules.test_drives.application.use_cases.admin.get_test_drives import GetTestDrivesAdminUseCase


def get_test_drive_admin_usecase(
    repo=Depends(get_test_drive_repository)
):
    return GetTestDrivesAdminUseCase(repo)

from modules.applications.api.dependencies import get_notification_service
from modules.test_drives.application.use_cases.admin.update_test_drive_status import UpdateTestDriveStatusUseCase
from modules.applications.api.dependencies import get_event_repository
def get_update_test_drive_status_usecase(
    repository=Depends(get_test_drive_repository),
    notification_service=Depends(get_notification_service),
    event_repository=Depends(get_event_repository)
):
    return UpdateTestDriveStatusUseCase(
        repository=repository,
        notification_service=notification_service,
        event_repository=event_repository
    )

from modules.test_drives.application.use_cases.admin.get_test_drive_details import GetTestDriveDetailsUseCase

def get_test_drive_detail_usecase(
    repository=Depends(get_test_drive_repository),
):
    return GetTestDriveDetailsUseCase(
        repository=repository
    )
from modules.test_drives.application.use_cases.get_my_test_drives import GetMyTestDrivesUseCase

def get_my_test_drives_usecase(
    repository=Depends(get_test_drive_repository)
):
    return GetMyTestDrivesUseCase(repository)

from modules.test_drives.application.use_cases.get_test_drive_details_client import GetTestDriveDetailClientUseCase

def get_test_drive_detail_client_usecase(
    repository=Depends(get_test_drive_repository),
    event_repository=Depends(get_event_repository)
):
    return GetTestDriveDetailClientUseCase(
        repository=repository,
        event_repository=event_repository
    )