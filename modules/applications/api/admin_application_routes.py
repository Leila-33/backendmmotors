from fastapi import APIRouter, Depends, Query
from modules.applications.application.use_cases.get_applications import (
    GetApplicationsUseCase
)
from modules.applications.application.use_cases.admin.update_application_status import UpdateApplicationStatusUseCase
from modules.applications.application.use_cases.admin.archive_application import ArchiveApplicationUseCase
from modules.applications.application.use_cases.admin.unarchive_application import UnarchiveApplicationUseCase
from modules.applications.application.use_cases.admin.soft_delete_application import SoftDeleteApplicationUseCase
from modules.applications.application.use_cases.admin.restore_cancelled_application import RestoreCancelledApplicationUseCase

from modules.applications.api.schemas import (
    GetApplicationsDTO,
    GetApplicationsResponse,
    UpdateDocumentDTO,
    UpdateDocumentResponseDTO,
    UpdateApplicationStatusDTO,
    UpdateApplicationStatusResponseDTO,
    ApplicationRestoreCancelledResponse,
    ApplicationActionResponse
    )
from modules.applications.api.dependencies import (
    get_update_document_usecase,
    get_update_application_status_usecase,
    get_get_applications_usecase,
    get_application_list_response_factory,
    get_restore_cancelled_usecase,
    get_archive_application_usecase,
    get_unarchive_application_usecase,
    get_soft_delete_application_usecase
)

from core.security.dependencies import get_current_admin
from modules.applications.api.application_list_response_factory import ApplicationListResponseFactory
from modules.auth.domain.entities.user import User

router = APIRouter(tags=["Admin Applications"])


# =========================
# GET APPLICATIONS
# =========================
@router.get(
    "",
    response_model=GetApplicationsResponse
)
def get_applications(

    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    search: str | None = None,
    status: str | None = None,
    application_type: str | None = None,

    sort: str = "created_at_desc",
    view_mode: str = "active",

    usecase: GetApplicationsUseCase = Depends(
        get_get_applications_usecase
    ),

    factory: ApplicationListResponseFactory = Depends(
        get_application_list_response_factory
    ),

    current_admin=Depends(get_current_admin)
):

    dto = GetApplicationsDTO(
        page=page,
        limit=limit,
        search=search,
        status=status,
        application_type=application_type,
        sort=sort,
        view_mode=view_mode
    )


    result = usecase.execute(
        dto=dto,
        role=current_admin.role,
        user_id=None
    )
    return factory.build(
        result=result,
        role=current_admin.role
    )



# =========================
# RESTORE
# =========================
@router.patch(
    "/{application_id}/restore-cancelled",
    response_model=ApplicationRestoreCancelledResponse
)
def restore_cancelled_application(
    application_id: str,
    current_admin: User = Depends(get_current_admin),
    usecase: RestoreCancelledApplicationUseCase = Depends(
        get_restore_cancelled_usecase
    )
):

    application = usecase.execute(
        application_id=application_id
    )

    return ApplicationRestoreCancelledResponse(
        id=application.id,
        status=application.status,
        message="Application restaurée avec succès"
    )


# =========================
# ARCHIVE
# =========================
@router.patch(
    "/{application_id}/archive",
    response_model=ApplicationActionResponse,
)
def archive_application(
    application_id: str,
    current_admin: User = Depends(get_current_admin),
    usecase: ArchiveApplicationUseCase = Depends(
        get_archive_application_usecase
    ),
):

    application = usecase.execute(
        application_id=application_id,
        current_admin=current_admin,
    )

    return ApplicationActionResponse(
        id=application.id,
        status=application.status,
        message="Dossier archivé avec succès.",
    )



# =========================
# UNARCHIVE
# =========================
@router.patch(
    "/{application_id}/unarchive",
    response_model=ApplicationActionResponse,
)
def unarchive_application(
    application_id: str,

    current_admin: User = Depends(
        get_current_admin
    ),

    usecase: UnarchiveApplicationUseCase = Depends(
        get_unarchive_application_usecase
    ),
):

    application = usecase.execute(
        application_id=application_id,
        current_admin=current_admin,
    )

    return ApplicationActionResponse(
        id=application.id,
        status=application.status,
        message="Dossier restauré depuis les archives avec succès.",
    )

# =====================================================
#  UPDATE DOCUMENT STATUS
# =====================================================
@router.patch("/documents/status", response_model=UpdateDocumentResponseDTO)
async def update_document_status(
    dto: UpdateDocumentDTO,
    use_case=Depends(get_update_document_usecase),
    current_admin=Depends(get_current_admin)
):

    return await use_case.execute(dto, current_admin)


# =====================================================
#  UPDATE APPLICATION STATUS
# =====================================================
@router.patch(
    "/{application_id}/status",
    response_model=UpdateApplicationStatusResponseDTO
)
async def update_application_status(

    application_id: str,

    dto: UpdateApplicationStatusDTO,

    usecase: UpdateApplicationStatusUseCase = Depends(
        get_update_application_status_usecase
    ),

    current_admin = Depends(
        get_current_admin
    )

):

    return await usecase.execute(
        application_id=application_id,
        dto=dto
    )

# =========================
# SOFT DELETE
# =========================
@router.delete(
    "/{application_id}",
    response_model=ApplicationActionResponse,
)
def soft_delete_application(
    application_id: str,

    current_admin: User = Depends(
        get_current_admin
    ),

    usecase: SoftDeleteApplicationUseCase = Depends(
        get_soft_delete_application_usecase
    ),
):

    application = usecase.execute(
        application_id=application_id,
        current_admin=current_admin,
    )

    return ApplicationActionResponse(
        id=application.id,
        status=application.status,
        message="Dossier supprimé avec succès.",
    )



















