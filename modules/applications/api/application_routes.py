from fastapi import APIRouter, Depends, Query

from modules.applications.application.use_cases.save_draft_application import (
    SaveDraftApplicationUseCase
)
from modules.applications.application.use_cases.get_application_by_vehicle import (
    GetApplicationByVehicleUseCase
)
from modules.applications.application.use_cases.delete_application import (DeleteApplicationUseCase)
from modules.applications.application.use_cases.get_applications import GetApplicationsUseCase
from modules.applications.application.use_cases.get_applications import (
    GetApplicationsUseCase
)
from modules.applications.application.use_cases.get_application import GetApplicationUseCase
from modules.applications.application.use_cases.cancel_application import CancelApplicationUseCase
from modules.applications.application.use_cases.submit_application import SubmitApplicationUseCase


from modules.auth.domain.entities.user import User
from core.security.dependencies import get_current_user


from modules.applications.api.application_list_response_factory import ApplicationListResponseFactory
from modules.applications.api.application_response_factory import ApplicationResponseFactory
from modules.applications.api.schemas import (
    SaveDraftApplicationDTO,
    GetApplicationsResponse,
    SubmitApplicationDTO,
    ApplicationCancelResponse,
    SaveDraftApplicationResponse,
    ApplicationDetailResponse,
    ApplicationByVehicleResponse,
    GetApplicationsDTO
)

from modules.auth.infrastructure.db.user_model import (UserModel)
from modules.applications.api.dependencies import (
    get_save_draft_application_usecase,
    get_application_by_vehicle_usecase,
    get_delete_application_usecase,
    get_get_applications_usecase,
    get_submit_application_usecase,
    get_cancel_application_usecase,
    get_application_response_factory,
    get_application_usecase,
    get_application_list_response_factory
    )
router = APIRouter(tags=["Applications"])


@router.post(
    "/draft",
    response_model=SaveDraftApplicationResponse,
)
def save_or_update_draft_application(
    dto: SaveDraftApplicationDTO,

    current_user: UserModel = Depends(
        get_current_user
    ),

    usecase: SaveDraftApplicationUseCase = Depends(
        get_save_draft_application_usecase
    ),
):

    result = usecase.execute(
        dto,
        current_user=current_user
    )

    return SaveDraftApplicationResponse(
        id=result.id,
        status=result.status,
    )

@router.post(
    "/submit",
    response_model=SaveDraftApplicationResponse,
)
def submit_application(
    dto: SubmitApplicationDTO,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: SubmitApplicationUseCase = Depends(
        get_submit_application_usecase
    ),
):

    result = usecase.execute(
        dto,
        current_user=current_user,
    )

    return SaveDraftApplicationResponse(
        id=result.id,
        status=result.status,
    )

@router.get(
    "/by-vehicle/{vehicle_id}",
    response_model=ApplicationByVehicleResponse | None,
)
def get_application_by_vehicle(
    vehicle_id: str,
    current_user: UserModel = Depends(get_current_user),
    usecase: GetApplicationByVehicleUseCase = Depends(
        get_application_by_vehicle_usecase
    ),
):

    application = usecase.execute(
        vehicle_id=vehicle_id,
        current_user=current_user,
    )

    if application is None:
        return None

    return ApplicationByVehicleResponse(
        id=application.id,
        status=application.status,
    )





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
    view_mode: str = "active",

    usecase: GetApplicationsUseCase = Depends(
        get_get_applications_usecase
    ),

    factory: ApplicationListResponseFactory = Depends(
        get_application_list_response_factory
    ),

    current_user=Depends(get_current_user)
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
        role=current_user.role,
        user_id=current_user.id
    )


    return factory.build(
        result=result,
        role=current_user.role
    )




@router.get("/{id}", response_model=ApplicationDetailResponse)
def get_application(
    id: str,
    usecase: GetApplicationUseCase = Depends(
        get_application_usecase
    ),
    factory: ApplicationResponseFactory = Depends(
        get_application_response_factory
    ),
    current_user=Depends(get_current_user)

):

    application, payment = usecase.execute(
        id, current_user
    )

    return factory.build(
        application,
        payment
    )





@router.delete("/{application_id}")
def delete_application(
    application_id: str,
    usecase: DeleteApplicationUseCase = Depends(get_delete_application_usecase),
    current_user=Depends(get_current_user)
):

    return usecase.execute(application_id, current_user)








@router.patch(
    "/{application_id}/cancel",
    response_model=ApplicationCancelResponse
)
def cancel_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    usecase: CancelApplicationUseCase = Depends(
        get_cancel_application_usecase
    )
):

    application = usecase.execute(
        application_id=application_id,
        role=current_user.role,
        user_id=current_user.id
    )

    return ApplicationCancelResponse(
        id=application.id,
        status=application.status,
        message="Application annulée avec succès"
    )


