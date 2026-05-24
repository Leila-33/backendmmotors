from fastapi import APIRouter, Depends
from modules.applications.application.use_cases.get_applications import (
    GetApplicationsUseCase
)
from modules.applications.application.use_cases.admin.update_document import (
    UpdateDocumentUseCase
)
from modules.applications.api.schemas import (
    GetApplicationsDTO,
    GetApplicationsResponse,
    UpdateDocumentDTO,
    UpdateApplicationStatusDTO,
    UpdateApplicationStatusResponseDTO
    )
from modules.applications.application.use_cases.admin.update_application_status import UpdateApplicationStatusUseCase
from modules.applications.api.dependencies import (
    get_update_document_usecase,
    get_update_application_status_usecase,
    get_soft_delete_usecase,
)
from modules.core.enums import DocumentStatus
from core.security.dependencies import get_current_admin

router = APIRouter(tags=["AdminApplications"])



















@router.patch("/documents/status")
def update_document_status(
    dto: UpdateDocumentDTO,
    use_case=Depends(get_update_document_usecase),
    current_admin=Depends(get_current_admin)
):

    return use_case.execute(dto, current_admin)




















# =====================================================
#  VALIDER DOSSIER
# =====================================================
@router.patch(
    "/{application_id}/status",
    response_model=UpdateApplicationStatusResponseDTO
)
def update_application_status(

    application_id: str,

    dto: UpdateApplicationStatusDTO,

    usecase: UpdateApplicationStatusUseCase = Depends(
        get_update_application_status_usecase
    ),

    current_admin = Depends(
        get_current_admin
    )

):

    return usecase.execute(
        application_id=application_id,
        dto=dto
    )







from modules.applications.api.dependencies import (
    get_archive_usecase,
    get_unarchive_usecase,
)



# =========================
# ARCHIVE
# =========================
@router.patch("/{application_id}/archive")
def archive_application(
    application_id: str,
    usecase = Depends(get_archive_usecase),
    current_admin = Depends(get_current_admin)
):

    return usecase.execute(application_id, current_admin)


# =========================
# UNARCHIVE
# =========================
@router.patch("/{application_id}/unarchive")
def unarchive_application(
    application_id: str,
    usecase = Depends(get_unarchive_usecase),
    current_admin = Depends(get_current_admin)
):

    return usecase.execute(application_id, current_admin)


# =========================
# DELETE (SOFT DELETE)
# =========================
@router.delete("/soft_delete/{application_id}")
def soft_delete_application(
    application_id: str,
    usecase = Depends(get_soft_delete_usecase),
    admin = Depends(get_current_admin)
):

    return usecase.execute(application_id)




from fastapi import APIRouter, Depends, Query


from modules.applications.api.dependencies import get_applications_usecase
@router.get(
    "",
    response_model=GetApplicationsResponse
)
def get_applications(

    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    search: str | None = None,
    status: str | None = None,

    # ⚠️ rename type → application_type (IMPORTANT)
    application_type: str | None = None,

    sort: str = "created_at_desc",

    archived: bool | None = None,

    usecase: GetApplicationsUseCase = Depends(get_applications_usecase),
    current_admin=Depends(get_current_admin)
):

    dto = GetApplicationsDTO(

        page=page,
        limit=limit,
        search=search,
        status=status,
        type=application_type,
        sort=sort,
        archived=archived
    )

    return usecase.execute(
        dto=dto,
        role="admin",
        user_id=None
    )
