from fastapi import APIRouter, Depends

from modules.applications.application.use_cases.save_draft_application_use_case import (
    SaveDraftApplicationUseCase
)
from modules.applications.application.use_cases.get_application_by_vehicle import (
    GetApplicationByVehicleUseCase
)
from modules.applications.application.use_cases.delete_application import (DeleteApplicationUseCase)


from core.security.dependencies import get_current_user

from modules.applications.api.schemas import (
    SaveDraftApplicationDTO,
    GetApplicationsResponse,
    SubmitApplicationDTO,
)
from modules.auth.infrastructure.db.user_model import (UserModel)
from modules.applications.api.dependencies import (
    get_save_draft_use_case,
    get_application_by_vehicle_usecase,
    get_delete_application_usecase,
    get_applications_usecase,
    get_submit_usecase
    )
router = APIRouter(tags=["Applications"])

@router.post("/draft")
def save_or_update_draft_application(
    dto: SaveDraftApplicationDTO,

    current_user: UserModel = Depends(get_current_user),

    usecase: SaveDraftApplicationUseCase = Depends(
        get_save_draft_use_case
    ),
):

    result = usecase.execute(
        dto,
        current_user=current_user
    )

    return {
        "id": result.id,
        "status": result.status
    }



@router.get("/by-vehicle/{vehicle_id}")
def get_application_by_vehicle(
    vehicle_id: str,
    current_user: UserModel = Depends(get_current_user),
    usecase: GetApplicationByVehicleUseCase = Depends(
        get_application_by_vehicle_usecase
    )
):

    application = usecase.execute(
        vehicle_id=vehicle_id,
        current_user=current_user
    )

    if not application:
        return None

    return {
        "id": application.id,
        "status": application.status
    }



from fastapi import Query



@router.get(
    "/me",
    response_model=GetApplicationsResponse
)
def get_applications(

    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),

    search: str | None = None,
    status: str | None = None,
    application_type: str | None = None,

    sort: str = "created_at_desc",
    archived: bool | None = None,

    usecase: GetApplicationsUseCase = Depends(get_applications_usecase),
    current_user=Depends(get_current_user)
):

    dto = GetApplicationsDTO(
        page=page,
        limit=limit,
        search=search,
        status=status,
        application_type=application_type,
        sort=sort,
        archived=archived
    )

    return usecase.execute(
        dto=dto,
        role="client",
        user_id=current_user.id
    )


# =========================
# IMPORTS
# =========================






from modules.applications.application.use_cases.get_application import (
    GetApplicationUseCase
)

from modules.applications.api.dependencies import (
    get_application_usecase
)



# =========================
# ROUTE
# =========================
@router.get("/{application_id}")
def get_application(
    application_id: str,
    current_user: UserModel = Depends(get_current_user),
    usecase: GetApplicationUseCase = Depends(
        get_application_usecase
    )
):

    application = usecase.execute(
        application_id=application_id,
        current_user=current_user
    )

    return application




# =========================
# ROUTE
# =========================
@router.delete("/{application_id}")
def delete_application(
    application_id: str,
    usecase: DeleteApplicationUseCase = Depends(get_delete_application_usecase),
    current_user=Depends(get_current_user)
):

    return usecase.execute(application_id, current_user)



# =========================================
# GET APPLICATIONS
# =========================================





from modules.applications.application.use_cases.get_applications import (
    GetApplicationsUseCase
)

from modules.applications.api.schemas import (
    GetApplicationsDTO
)








from modules.applications.application.use_cases.submit_application import SubmitApplicationUseCase



@router.post("/submit")
def submit_application(
    dto: SubmitApplicationDTO,
    current_user=Depends(get_current_user),
    usecase: SubmitApplicationUseCase = Depends(get_submit_usecase)
):

    result = usecase.execute(
        dto=dto,
        current_user=current_user
    )

    return result