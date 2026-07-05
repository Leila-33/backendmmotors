
from fastapi import APIRouter, Depends

from modules.test_drives.api.dependencies import (
    get_test_drive_admin_usecase,
    get_test_drive_detail_usecase
)

from modules.core.infrastructure.dependencies import (
        get_test_drive_repository
)

router = APIRouter(tags=["AdminTestDrive"])


from core.security.dependencies import get_current_admin


@router.get("pending-count")
def get_pending_count(
    current_admin = Depends(get_current_admin),
    repo = Depends(get_test_drive_repository)
):

    return {
        "count": repo.count_pending()
    }

@router.get("")
def get_test_drives(
    current_admin=Depends(get_current_admin),
    usecase=Depends(get_test_drive_admin_usecase)
):

    return usecase.execute()






from modules.test_drives.api.dependencies import get_update_test_drive_status_usecase

from modules.test_drives.api.schemas import UpdateTestDriveStatusDTO

@router.post("/{test_drive_id}/status")
async def update_test_drive_status(

    test_drive_id: str,

    dto: UpdateTestDriveStatusDTO,

    current_admin=Depends(get_current_admin),

    usecase=Depends(get_update_test_drive_status_usecase)
):

    result = await usecase.execute(
        test_drive_id=test_drive_id,
        status=dto.status,
        actor_id=current_admin.id,
        actor_role="admin"
    )

    return {
        "success": True,
        "status": result.status
    }




@router.get("/{test_drive_id}")
def get_test_drive_details(
    test_drive_id: str,
    current_admin=Depends(get_current_admin),
    usecase=Depends(get_test_drive_detail_usecase),
):

    result = usecase.execute(test_drive_id)

    return result