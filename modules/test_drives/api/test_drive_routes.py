from fastapi import APIRouter, Depends

from core.security.dependencies import get_current_user

from modules.auth.infrastructure.db.user_model import UserModel
from modules.test_drives.domain.enums import TestDriveStatus

from modules.test_drives.api.schemas import CreateTestDriveDTO
from modules.test_drives.application.use_cases.create_test_drive import CreateTestDriveUseCase
from modules.test_drives.application.use_cases.get_avaibility import GetAvailabilityUseCase

from modules.test_drives.api.dependencies import (
    get_create_test_drive_usecase,
    get_availability_usecase,
    get_update_test_drive_status_usecase
)

router = APIRouter(tags=["TestDrive"])

@router.post("")
def create_test_drive(
    dto: CreateTestDriveDTO,

    current_user: UserModel = Depends(
        get_current_user
    ),

    usecase: CreateTestDriveUseCase = Depends(
        get_create_test_drive_usecase
    )
):

    result = usecase.execute(
        dto,
        current_user
    )

    return {
        "id": result.id,
        "status": result.status
    }

@router.get("/availability")
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

from modules.test_drives.api.dependencies import get_my_test_drives_usecase

@router.get("/me")
def get_my_test_drives(
    current_user=Depends(get_current_user),
    usecase=Depends(get_my_test_drives_usecase)
):
    return usecase.execute(current_user.id)
from modules.test_drives.api.dependencies import get_test_drive_detail_client_usecase

@router.get("/{test_drive_id}")
def get_test_drive_detail(
    test_drive_id: str,
    current_user=Depends(get_current_user),
    usecase=Depends(get_test_drive_detail_client_usecase)
):
    return usecase.execute(test_drive_id, current_user.id)

@router.post("/{test_drive_id}/cancel")
async def cancel_test_drive(

    test_drive_id: str,

    current_user=Depends(get_current_user),

    usecase=Depends(get_update_test_drive_status_usecase)
):

    result = await usecase.execute(
        test_drive_id=test_drive_id,
        status=TestDriveStatus.CANCELLED,
        actor_id=current_user.id,
        actor_role="client"
    )

    return {
        "success": True,
        "status": result.status
    }