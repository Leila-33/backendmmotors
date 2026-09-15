from fastapi import APIRouter, Depends, Query
from typing import Annotated

# =========================
# CORE
# =========================

from core.security.dependencies import get_current_admin


# =========================
# DEPENDENCIES
# =========================

from modules.test_drives.api.dependencies import (
    get_update_test_drive_status_usecase,
    get_pending_test_drive_count_usecase,
    get_get_test_drives_admin_usecase,
)


# =========================
# USE CASES
# =========================

from modules.test_drives.application.use_cases.admin.get_test_drives_admin import (
    GetTestDrivesAdminUseCase,
)

from modules.test_drives.application.use_cases.update_test_drive_status import (
    UpdateTestDriveStatusUseCase,
)


# =========================
# DTO
# =========================

from modules.test_drives.application.dtos.admin.get_test_drives_admin_dto import (
    GetTestDrivesAdminDTO,
)

from modules.test_drives.application.dtos.update_test_drive_status_dto import (
    UpdateTestDriveStatusDTO,
)


# =========================
# SCHEMAS
# =========================

from modules.test_drives.api.schemas import (
    GetTestDrivesAdminQuery,
    PaginatedTestDriveAdminResponse,
    UpdateTestDriveStatusRequest,
    TestDriveStatusResponse,
    PendingTestDriveCountResponse,
)


# =========================
# MAPPERS
# =========================

from modules.test_drives.infrastructure.mappers.test_drive_mapper import (
    TestDriveMapper,
)

from modules.test_drives.infrastructure.mappers.test_drive_admin_list_mapper import (
    TestDriveAdminListMapper,
)


router = APIRouter(
    tags=["AdminTestDrive"]
)


# =====================================================
# PENDING COUNT
# =====================================================

@router.get(
    "/pending-count",
    response_model=PendingTestDriveCountResponse,
)
def get_pending_count(
    current_admin=Depends(get_current_admin),
    use_case=Depends(
        get_pending_test_drive_count_usecase
    ),
):

    result = use_case.execute()

    return PendingTestDriveCountResponse(
        count=result.count
    )


# =====================================================
# LIST
# =====================================================

@router.get(
    "",
    response_model=PaginatedTestDriveAdminResponse,
)
def get_test_drives_admin(
    query: Annotated[
        GetTestDrivesAdminQuery,
        Query(),
    ],

    current_admin=Depends(
        get_current_admin
    ),

    use_case: GetTestDrivesAdminUseCase = Depends(
        get_get_test_drives_admin_usecase
    ),
):


    dto = GetTestDrivesAdminDTO(
        status=query.status,
        search=query.search,
        date=query.date,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
        page=query.page,
        limit=query.limit,
    )

    result = use_case.execute(dto)

    # =========================
    # RÉPONSE
    # =========================

    return TestDriveAdminListMapper.to_paginated_response(
        result
    )

# =====================================================
# UPDATE STATUS
# =====================================================

@router.post(
    "/{test_drive_id}/status",
    response_model=TestDriveStatusResponse,
)
async def update_test_drive_status(
    test_drive_id: str,

    data: UpdateTestDriveStatusRequest,

    current_admin=Depends(
        get_current_admin
    ),

    use_case: UpdateTestDriveStatusUseCase = Depends(
        get_update_test_drive_status_usecase
    ),
):

    dto = UpdateTestDriveStatusDTO(
        test_drive_id=test_drive_id,
        status=data.status,
        actor_id=current_admin.id,
        actor_role=current_admin.role,
    )

    test_drive = await use_case.execute(dto)

    return TestDriveStatusResponse(
        id=test_drive.id,
        status=test_drive.status.value,
        appointment_date=test_drive.appointment_date,
        message="Statut de l’essai routier mis à jour",
    )