from fastapi import APIRouter, Depends, status

from core.security.dependencies import get_current_user

from modules.test_drives.api.schemas import (
    CreateTestDriveRequest,
    TestDriveResponse,
    GetAvailabilityRequest,
    GetAvailabilityResponse,
    MyTestDriveResponse,
    TestDriveDetailResponse,
    TestDriveStatusResponse,
)

from modules.test_drives.application.dtos.create_test_drive_dto import (
    CreateTestDriveDTO,
)
from modules.test_drives.application.dtos.get_availability_dto import (
    GetAvailabilityDTO,
)
from modules.test_drives.application.dtos.update_test_drive_status_dto import (
    UpdateTestDriveStatusDTO,
)

from modules.test_drives.application.use_cases.create_test_drive import (
    CreateTestDriveUseCase,
)
from modules.test_drives.application.use_cases.get_availability import (
    GetAvailabilityUseCase,
)
from modules.test_drives.application.use_cases.get_my_test_drives import (
    GetMyTestDrivesUseCase,
)
from modules.test_drives.application.use_cases.get_test_drive_detail import (
    GetTestDriveDetailUseCase,
)
from modules.test_drives.application.use_cases.update_test_drive_status import (
    UpdateTestDriveStatusUseCase,
)

from modules.test_drives.api.dependencies import (
    get_create_test_drive_usecase,
    get_get_availability_usecase,
    get_my_test_drives_usecase,
    get_test_drive_detail_usecase,
    get_update_test_drive_status_usecase,
)

from modules.test_drives.domain.enums import TestDriveStatus

from modules.test_drives.infrastructure.mappers.test_drive_mapper import (
    TestDriveMapper,
)
from modules.test_drives.infrastructure.mappers.my_test_drive_mapper import (
    MyTestDriveMapper,
)


router = APIRouter(
    tags=["TestDrive"]
)


# =====================================================
# CREATE TEST DRIVE
# =====================================================

@router.post(
    "",
    response_model=TestDriveResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test_drive(
    payload: CreateTestDriveRequest,
    current_user=Depends(get_current_user),
    use_case: CreateTestDriveUseCase = Depends(
        get_create_test_drive_usecase
    ),
):

    dto = CreateTestDriveDTO(
        vehicle_id=payload.vehicle_id,
        appointment_date=payload.appointment_date,
        comment=payload.comment,
    )

    result = use_case.execute(
        dto=dto,
        user_id=current_user.id,
    )

    return TestDriveMapper.to_response(
        result.test_drive
    )


# =====================================================
# AVAILABILITY
# =====================================================

@router.get(
    "/availability",
    response_model=GetAvailabilityResponse,
)
def get_availability(
    request: GetAvailabilityRequest,
    use_case: GetAvailabilityUseCase = Depends(
        get_get_availability_usecase
    ),
):

    dto = GetAvailabilityDTO(
        vehicle_id=request.vehicle_id,
        date=request.date,
    )

    result = use_case.execute(dto)

    return GetAvailabilityResponse(
        date=result.date,
        timezone=result.timezone,
        available_slots=result.available_slots,
    )


# =====================================================
# MY TEST DRIVES
# =====================================================

@router.get(
    "/me",
    response_model=list[MyTestDriveResponse],
)
def get_my_test_drives(
    current_user=Depends(get_current_user),
    use_case: GetMyTestDrivesUseCase = Depends(
        get_my_test_drives_usecase
    ),
):

    result = use_case.execute(
        user_id=current_user.id
    )

    return [
        MyTestDriveMapper.to_response(test_drive)
        for test_drive in result.items
    ]


# =====================================================
# TEST DRIVE DETAIL
# =====================================================

@router.get(
    "/{test_drive_id}",
    response_model=TestDriveDetailResponse,
)
def get_test_drive_detail(
    test_drive_id: str,
    current_user=Depends(get_current_user),
    use_case: GetTestDriveDetailUseCase = Depends(
        get_test_drive_detail_usecase
    ),
):

    result = use_case.execute(
        test_drive_id=test_drive_id,
        user_id=current_user.id,
        user_role=current_user.role,
    )

    return TestDriveMapper.to_detail_response(
        result.test_drive,
        result.events,
    )


# =====================================================
# CANCEL TEST DRIVE
# =====================================================

@router.post(
    "/{test_drive_id}/cancel",
    response_model=TestDriveStatusResponse,
)
async def cancel_test_drive(
    test_drive_id: str,
    current_user=Depends(get_current_user),
    use_case: UpdateTestDriveStatusUseCase = Depends(
        get_update_test_drive_status_usecase
    ),
):

    dto = UpdateTestDriveStatusDTO(
        test_drive_id=test_drive_id,
        status=TestDriveStatus.CANCELLED,
        actor_id=current_user.id,
        actor_role=current_user.role,
    )

    result = await use_case.execute(dto)

    test_drive = result.test_drive

    return TestDriveStatusResponse(
        id=test_drive.id,
        status=test_drive.status.value,
        appointment_date=test_drive.appointment_date,
        message="Essai routier annulé",
    )