from fastapi import APIRouter, Depends, status

from core.security.dependencies import get_current_user
from modules.test_drives.infrastructure.mappers.test_drive_mapper import TestDriveMapper
from modules.test_drives.domain.enums import TestDriveStatus

# =========================
# SCHEMAS
# =========================
from modules.test_drives.api.schemas import (
    CreateTestDriveRequest,
    TestDriveResponse,
    AvailabilityResponse,
    MyTestDriveResponse,
    TestDriveDetailClientResponse,
    TestDriveStatusResponse
)
# =========================
# USE CASES
# =========================
from modules.test_drives.application.use_cases.create_test_drive import CreateTestDriveUseCase
from modules.test_drives.application.use_cases.get_avaibility import GetAvailabilityUseCase

# =========================
# DEPENDENCIES
# =========================
from modules.test_drives.api.dependencies import (
    get_create_test_drive_usecase,
    get_availability_usecase,
    get_update_test_drive_status_usecase,
    get_my_test_drives_usecase,
    get_test_drive_detail_client_usecase
)

# =========================
# MAPPERS
# =========================
from modules.test_drives.infrastructure.mappers.my_test_drive_mapper import (
    MyTestDriveMapper
)
from modules.test_drives.infrastructure.mappers.test_drive_detail_client_mapper import TestDriveDetailClientMapper

router = APIRouter(tags=["TestDrive"])



@router.post(
    "",
    response_model=TestDriveResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test_drive(
    data: CreateTestDriveRequest,
    current_user=Depends(get_current_user),
    usecase=Depends(get_create_test_drive_usecase),
):

    test_drive = usecase.execute(
        data,
        current_user,
    )

    return TestDriveMapper.to_response(
        test_drive
    )

@router.get("/availability", response_model=AvailabilityResponse
)
def get_availability(
    vehicle_id: str,
    date: str,
    usecase: GetAvailabilityUseCase = Depends(
        get_availability_usecase
    )
):

    return usecase.execute(
        vehicle_id=vehicle_id,
        date=date
    )


@router.get(
    "/me",
    response_model=list[MyTestDriveResponse]
)
def get_my_test_drives(
    current_user=Depends(get_current_user),
    usecase=Depends(get_my_test_drives_usecase),
):

    test_drives = usecase.execute(
        current_user.id
    )

    return [
        MyTestDriveMapper.to_response(td)
        for td in test_drives
    ]


@router.get(
    "/{test_drive_id}",
    response_model=TestDriveDetailClientResponse
)
def get_test_drive_detail(
    test_drive_id: str,
    current_user=Depends(get_current_user),
    usecase=Depends(
        get_test_drive_detail_client_usecase
    ),
):

    result = usecase.execute(
        test_drive_id,
        current_user.id
    )


    return TestDriveDetailClientMapper.to_response(
        result["test_drive"],
        result["events"]
    )

@router.post("/{test_drive_id}/cancel")
async def cancel_test_drive(

    test_drive_id: str,

    current_user=Depends(get_current_user),

    usecase=Depends(get_update_test_drive_status_usecase)
):

    test_drive = await usecase.execute(
        test_drive_id=test_drive_id,
        status=TestDriveStatus.CANCELLED,
        actor_id=current_user.id,
        actor_role="client"
    )

    
    return TestDriveStatusResponse(
        id=test_drive.id,
        status=test_drive.status.value,
        appointment_date=test_drive.appointment_date,
        message="Statut de l’essai routier mis à jour"
    )