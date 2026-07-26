
from fastapi import APIRouter, Depends
# =========================
# CORE
# =========================
from core.security.dependencies import get_current_admin

# =========================
# DEPENDENCIES
# =========================
from modules.test_drives.api.dependencies import (
    get_test_drives_admin_usecase,
    get_test_drive_detail_usecase,
    get_update_test_drive_status_usecase,
    get_pending_test_drive_count_usecase
)


# =========================
# SCHEMAS
# =========================
from modules.test_drives.api.schemas import (
    TestDriveDetailsAdminResponse,
    TestDriveAdminListResponse,
    UpdateTestDriveStatusRequest,
    TestDriveStatusResponse,
    PendingTestDriveCountResponse
)

# =========================
# MAPPER
# =========================
from modules.test_drives.infrastructure.mappers.test_drive_detail_admin_mapper import TestDriveDetailAdminMapper
from modules.test_drives.infrastructure.mappers.test_drive_admin_list_mapper import TestDriveAdminListMapper

router = APIRouter(tags=["AdminTestDrive"])



@router.get(
    "/pending-count",
    response_model=PendingTestDriveCountResponse
)
def get_pending_count(
    current_admin=Depends(get_current_admin),
    use_case=Depends(get_pending_test_drive_count_usecase)
):

    return use_case.execute()



@router.get(
    "",
    response_model=TestDriveAdminListResponse
)
def get_test_drives(
    status: str | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 20,
    use_case=Depends(get_test_drives_admin_usecase)
):

    result = use_case.execute(
        status=status,
        search=search,
        page=page,
        limit=limit
    )

    return TestDriveAdminListMapper.to_response(result)


@router.post(
    "/{test_drive_id}/status",
    response_model=TestDriveStatusResponse
)
async def update_test_drive_status(
    test_drive_id: str,
    data: UpdateTestDriveStatusRequest,
    current_user=Depends(get_current_admin),
    use_case=Depends(get_update_test_drive_status_usecase)
):

    test_drive = await use_case.execute(
        test_drive_id=test_drive_id,
        status=data.status,
        actor_id=current_user.id,
        actor_role=current_user.role
    )


    return TestDriveStatusResponse(
        id=test_drive.id,
        status=test_drive.status.value,
        appointment_date=test_drive.appointment_date,
        message="Statut de l’essai routier mis à jour"
    )




@router.get("/{test_drive_id}", response_model=TestDriveDetailsAdminResponse)
def get_test_drive_details(
    test_drive_id: str,
    current_admin=Depends(get_current_admin),
    usecase=Depends(get_test_drive_detail_usecase),
):

    result = usecase.execute(test_drive_id)

    return TestDriveDetailAdminMapper.to_response(result)

