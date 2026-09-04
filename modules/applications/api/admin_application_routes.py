from fastapi import APIRouter, Depends

# ============================================================
# Application — DTO
# ============================================================
from modules.applications.application.dtos.admin.update_application_status_dto import (
    UpdateApplicationStatusDTO
)
from modules.applications.application.dtos.admin.update_document_dto import (
    UpdateDocumentDTO
)
from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO
)
from modules.applications.application.dtos.get_applications_dto import (
    GetApplicationsDTO,
)


# ============================================================
# Application — Use Cases
# ============================================================

from modules.applications.application.use_cases.get_applications import (
    GetApplicationsUseCase,
)

from modules.applications.application.use_cases.admin.archive_application import (
    ArchiveApplicationUseCase,
)

from modules.applications.application.use_cases.admin.restore_cancelled_application import (
    RestoreCancelledApplicationUseCase,
)

from modules.applications.application.use_cases.admin.soft_delete_application import (
    SoftDeleteApplicationUseCase,
)

from modules.applications.application.use_cases.admin.unarchive_application import (
    UnarchiveApplicationUseCase,
)

from modules.applications.application.use_cases.admin.update_application_status import (
    UpdateApplicationStatusUseCase,
)

from modules.applications.application.use_cases.admin.update_document import (
    UpdateDocumentUseCase,
)
# ============================================================
# API — Schemas
# ============================================================

from modules.applications.api.schemas import (
    ApplicationActionResponse,
    GetApplicationsRequest,
    UpdateDocumentResponse,
    UpdateApplicationStatusRequest,
    UpdateDocumentRequest,
    GetApplicationsResponse
)


# ============================================================
# API — Dependencies
# ============================================================

from modules.applications.api.dependencies import (
    get_archive_application_usecase,
    get_application_list_response_factory,
    get_get_applications_usecase,
    get_restore_cancelled_usecase,
    get_soft_delete_application_usecase,
    get_unarchive_application_usecase,
    get_update_application_status_usecase,
    get_update_document_usecase,
)


# ============================================================
# API — Response Factory
# ============================================================

from modules.applications.api.application_list_response_factory import (
    ApplicationListResponseFactory,
)


# ============================================================
# Security
# ============================================================

from core.security.dependencies import get_current_admin


# ============================================================
# Domain
# ============================================================

from modules.auth.domain.entities.user import User


# ============================================================
# Router
# ============================================================

router = APIRouter(
    tags=["Admin Applications"],
)


# ============================================================
# GET APPLICATIONS
# ============================================================
@router.get(
    "",
    response_model=GetApplicationsResponse,
)
def get_applications(
    query: GetApplicationsRequest = Depends(),
    usecase: GetApplicationsUseCase = Depends(
        get_get_applications_usecase
    ),
    factory: ApplicationListResponseFactory = Depends(
        get_application_list_response_factory
    ),
    current_admin: User = Depends(get_current_admin),
):
    dto = GetApplicationsDTO(
        page=query.page,
        limit=query.limit,
        search=query.search,
        status=query.status,
        application_type=query.application_type,
        sort=query.sort,
        view_mode=query.view_mode,
    )

    result = usecase.execute(
        dto=dto,
        role=current_admin.role,
        user_id=None,
    )

    return factory.build(
        result=result,
        role=current_admin.role,
    )


# ============================================================
# RESTORE CANCELLED APPLICATION
# ============================================================

@router.patch(
    "/{application_id}/restore-cancelled",
    response_model=ApplicationActionResponse,
)
def restore_cancelled_application(
    application_id: str,
    current_admin: User = Depends(
        get_current_admin
    ),
    usecase: RestoreCancelledApplicationUseCase = Depends(
        get_restore_cancelled_usecase
    ),
):
    dto = ApplicationIdDTO(
    application_id=application_id
)

    application = usecase.execute(
        dto=dto,
        current_admin=current_admin
    )

    return ApplicationActionResponse(
        id=application.id,
        status=application.status,
        message="Application restaurée avec succès",
    )


# ============================================================
# ARCHIVE APPLICATION
# ============================================================

@router.patch(
    "/{application_id}/archive",
    response_model=ApplicationActionResponse,
)
def archive_application(
    application_id: str,
    current_admin: User = Depends(
        get_current_admin
    ),
    usecase: ArchiveApplicationUseCase = Depends(
        get_archive_application_usecase
    ),
):
    dto = ApplicationIdDTO(
        application_id=application_id
    )
    
    application = usecase.execute(
            dto=dto,
            current_admin=current_admin
        )

    return ApplicationActionResponse(
        id=application.id,
        status=application.status,
        message="Dossier archivé avec succès.",
    )


# ============================================================
# UNARCHIVE APPLICATION
# ============================================================

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
    dto = ApplicationIdDTO(
        application_id=application_id
    )
    
    application = usecase.execute(
            dto=dto,
            current_admin=current_admin
        )

    return ApplicationActionResponse(
        id=application.id,
        status=application.status,
        message="Dossier restauré depuis les archives avec succès.",
    )


# ============================================================
# UPDATE DOCUMENT STATUS
# ============================================================
@router.patch(
    "/documents/status",
    response_model=UpdateDocumentResponse,
)
async def update_document_status(
    request: UpdateDocumentRequest,
    usecase: UpdateDocumentUseCase = Depends(
        get_update_document_usecase
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    dto = UpdateDocumentDTO(
        document_id=request.document_id,
        status=request.status,
        comment=request.comment,
    )

    result = await usecase.execute(
        dto=dto,
        current_admin=current_admin,
    )

    return UpdateDocumentResponse(
        document_id=result.document_id,
        status=result.status,
        comment=result.comment,
    )


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

@router.patch(
    "/{application_id}/status",
    response_model=ApplicationActionResponse,
)
async def update_application_status(
    application_id: str,
    request: UpdateApplicationStatusRequest,
    usecase: UpdateApplicationStatusUseCase = Depends(
        get_update_application_status_usecase
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
):
    dto = UpdateApplicationStatusDTO(
        application_id=application_id,
        status=request.status,
        reason=request.reason
    )

    result = await usecase.execute(
        dto=dto,
        current_admin=current_admin,
    )

    return ApplicationActionResponse(
        id=result.id,
        status=result.status,
        message="Statut de l'application mis à jour avec succès.",
    )

# ============================================================
# SOFT DELETE APPLICATION
# ============================================================

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
    dto = ApplicationIdDTO(
            application_id=application_id
        )
    
    application = usecase.execute(
                dto=dto,
                current_admin=current_admin
            )

    return ApplicationActionResponse(
        id=application.id,
        status=application.status,
        message="Dossier supprimé avec succès.",
    )


















