from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from modules.applications.application.use_cases.admin.get_applications_admin import GetApplicationsAdmin
from modules.applications.application.use_cases.admin.approve_application import ApproveApplication
from modules.applications.application.use_cases.admin.reject_application import RejectApplication
from modules.applications.application.use_cases.admin.get_application_detail_admin import GetApplicationDetailAdmin

from modules.applications.application.use_cases.admin.get_applications_admin import GetApplicationsAdmin


from modules.applications.api.schemas import (
    RejectApplicationRequest,
    AdminApplicationDetailResponse,
    AdminApplicationListResponse,
    ApplicationActionResponse)

from modules.applications.api.dependencies import (
    get_application_repository,
    get_event_repository,
    get_notification_service,
    get_current_admin
)

from modules.clients.api.dependencies import get_user_repository
from modules.vehicles.api.dependencies import get_vehicle_repository

from modules.auth.dependencies import get_current_user  # 🔐 admin (à adapter)

router = APIRouter(prefix="/admin", tags=["Admin"])


# =====================================================
# 📌 LISTE DES DOSSIERS (avec filtres simples)
# =====================================================

@router.get(
    "/applications",
    response_model=AdminApplicationListResponse
)
def get_applications_admin(
    status: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    sort: Optional[str] = "createdAt_desc",
    page: int = 1,
    size: int = 10,
    repo=Depends(get_application_repository),
):

    use_case = GetApplicationsAdmin(repo)

    result = use_case.execute(
        filters={
            "status": status,
            "type": type,
            "search": search,
            "sort": sort
        },
        page=page,
        size=size
    )

    # 👉 validation Pydantic ici
    return AdminApplicationListResponse.model_validate(result)

# =====================================================
# 📌 DÉTAIL DOSSIER
# =====================================================





@router.get(
    "/applications/{application_id}",
    response_model=AdminApplicationDetailResponse
)
def get_application_detail_admin(
    application_id: str,
    repo=Depends(get_application_repository)
):

    use_case = GetApplicationDetailAdmin(repo)

    try:
        result = use_case.execute(application_id)
        return AdminApplicationDetailResponse.model_validate(result)

    except Exception as e:
        if str(e) == "APPLICATION_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Dossier introuvable")

        raise HTTPException(status_code=500, detail="Erreur serveur")


# =====================================================
# ✅ VALIDER DOSSIER
# =====================================================
@router.post("/admin/applications/{application_id}/approve", response_model=ApplicationActionResponse)
def approve_application(
    application_id: str,
    current_user=Depends(get_current_admin),
    application_repo=Depends(get_application_repository),
    event_repo=Depends(get_event_repository)
):

    use_case = ApproveApplication(application_repo, event_repo)

    try:
        result = use_case.execute(application_id, current_user.id)
        return ApplicationActionResponse(
        id=result["id"],
        status=result["status"],
        message=result["message"]
    )

    except Exception as e:

        if str(e) == "APPLICATION_NOT_FOUND":
            raise HTTPException(404, "Dossier introuvable")

        if str(e) == "APPLICATION_NOT_APPROVABLE":
            raise HTTPException(400, "Dossier non validable")

        raise HTTPException(500, "Erreur serveur")


# =====================================================
# ❌ REFUSER DOSSIER
# =====================================================



@router.post("/admin/applications/{application_id}/reject", response_model=ApplicationActionResponse)
def reject_application(
    application_id: str,
    data: RejectApplicationRequest,
    application_repo=Depends(get_application_repository),
    event_repo=Depends(get_event_repository),
    notification_service=Depends(get_notification_service),
    current_user=Depends(get_current_admin)
):

    use_case = RejectApplication(
        application_repo,
        event_repo,
        notification_service
    )

    try:
        result= use_case.execute(
            application_id=application_id,
            admin_id=current_user.id,
            reason=data.reason
        )
        return ApplicationActionResponse(
        id=result["id"],
        status=result["status"],
        message=result["message"]
    )

    except Exception as e:

        if str(e) == "APPLICATION_NOT_FOUND":
            raise HTTPException(404, "Dossier introuvable")

        if str(e) == "APPLICATION_NOT_REJECTABLE":
            raise HTTPException(400, "Dossier non refusables dans cet état")

        raise HTTPException(
            status_code=500,
            detail="Erreur lors du refus du dossier"
        )