from fastapi import APIRouter, Depends

# ============================================================
# Application — DTO
# ============================================================
from modules.applications.application.dtos.vehicle_id_dto import (
    VehicleIdDTO
)
from modules.applications.application.dtos.application_id_dto import (
    ApplicationIdDTO
)
from modules.applications.application.dtos.submit_application_dto import (
    SubmitApplicationDTO
)
from modules.applications.application.dtos.save_draft_application_dto import (
    SaveDraftApplicationDTO,
)
from modules.applications.application.dtos.financing_dto import (
    FinancingDTO,
)
from modules.applications.application.dtos.trade_in_dto import (
    TradeInDTO,
)
from modules.applications.application.dtos.document_dto import (
    DocumentDTO,
)
from modules.applications.application.dtos.selected_dates_dto import (
    SelectedDatesDTO,
)
from modules.applications.application.dtos.get_applications_dto import (
    GetApplicationsDTO,
)
# ============================================================
# Application — Use Cases
# ============================================================

from modules.applications.application.use_cases.cancel_application import (
    CancelApplicationUseCase,
)

from modules.applications.application.use_cases.delete_application import (
    DeleteApplicationUseCase,
)

from modules.applications.application.use_cases.get_application import (
    GetApplicationUseCase,
)

from modules.applications.application.use_cases.get_application_by_vehicle import (
    GetApplicationByVehicleUseCase,
)

from modules.applications.application.use_cases.get_applications import (
    GetApplicationsUseCase,
)

from modules.applications.application.use_cases.save_draft_application import (
    SaveDraftApplicationUseCase,
)

from modules.applications.application.use_cases.submit_application import (
    SubmitApplicationUseCase,
)


# ============================================================
# API — Dependencies
# ============================================================

from modules.applications.api.dependencies import (
    get_application_by_vehicle_usecase,
    get_application_list_response_factory,
    get_application_response_factory,
    get_application_usecase,
    get_cancel_application_usecase,
    get_delete_application_usecase,
    get_get_applications_usecase,
    get_save_draft_application_usecase,
    get_submit_application_usecase,
)


# ============================================================
# API — Response Factories
# ============================================================

from modules.applications.api.application_list_response_factory import (
    ApplicationListResponseFactory,
)

from modules.applications.api.application_response_factory import (
    ApplicationResponseFactory,
)


# ============================================================
# API — Schemas
# ============================================================

from modules.applications.api.schemas import (
    ApplicationByVehicleResponse,
    ApplicationActionResponse,
    ApplicationDetailResponse,
    GetApplicationsResponse,
    SaveDraftApplicationRequest,
    SubmitApplicationRequest,
    DeleteApplicationResponse,
    GetApplicationsRequest
)


# ============================================================
# Security
# ============================================================

from core.security.dependencies import (
    get_current_user,
)


# ============================================================
# Domain
# ============================================================

from modules.auth.domain.entities.user import User


# ============================================================
# Router
# ============================================================

router = APIRouter(
    tags=["Applications"]
)


# ============================================================
# CREATE / UPDATE DRAFT
# ============================================================

@router.post(
    "/draft",
    response_model=ApplicationActionResponse,
)
def save_or_update_draft_application(
    request: SaveDraftApplicationRequest,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: SaveDraftApplicationUseCase = Depends(
        get_save_draft_application_usecase
    ),
):

    # ========================================================
    # REQUEST → DTO
    # ========================================================

    dto = SaveDraftApplicationDTO(

        # ----------------------------------------------------
        # IDS
        # ----------------------------------------------------

        id=request.id,

        vehicle_id=request.vehicle_id,

        # ----------------------------------------------------
        # TYPE
        # ----------------------------------------------------

        application_type=request.application_type,

        # ----------------------------------------------------
        # USER INFOS
        # ----------------------------------------------------

        first_name=request.first_name,

        last_name=request.last_name,

        email=request.email,

        phone=request.phone,

        address=request.address,

        birth_date=request.birth_date,

        # ----------------------------------------------------
        # RENT
        # ----------------------------------------------------

        selected_dates=(
            SelectedDatesDTO(
                start=request.selected_dates.start,
                end=request.selected_dates.end,
            )
            if request.selected_dates
            else None
        ),

        # ----------------------------------------------------
        # FINANCIAL
        # ----------------------------------------------------

        monthly_income=request.monthly_income,

        monthly_expenses=request.monthly_expenses,

        employment_status=request.employment_status,

        # ----------------------------------------------------
        # OPTIONS
        # ----------------------------------------------------

        selected_option_ids=(
            request.selected_option_ids
        ),

        # ----------------------------------------------------
        # PRICE
        # ----------------------------------------------------

        total_price=request.total_price,

        # ----------------------------------------------------
        # FINANCING
        # ----------------------------------------------------

        financing=(
            FinancingDTO(
                down_payment=(
                    request.financing.down_payment
                ),
                duration_months=(
                    request.financing.duration_months
                ),
            )
            if request.financing
            else None
        ),

        # ----------------------------------------------------
        # TRADE-IN
        # ----------------------------------------------------

        trade_in=(
            TradeInDTO(
                enabled=request.trade_in.enabled,
                brand=request.trade_in.brand,
                model=request.trade_in.model,
                year=request.trade_in.year,
                mileage=request.trade_in.mileage,
                condition=request.trade_in.condition,
            )
            if request.trade_in
            else None
        ),

        # ----------------------------------------------------
        # DOCUMENTS
        # ----------------------------------------------------

        documents=[
            DocumentDTO(
                type=document.type,
                s3_key=document.s3_key,
            )
            for document in request.documents
        ],
    )

    # ========================================================
    # USE CASE
    # ========================================================

    result = usecase.execute(
        dto=dto,
        current_user_id=current_user.id,
    )

    # ========================================================
    # RESULT → RESPONSE
    # ========================================================

    return ApplicationActionResponse(
        id=result.id,
        status=result.status,
        message="Brouillon enregistré avec succès.",
    )

# ============================================================
# SUBMIT APPLICATION
# ============================================================

@router.post(
    "/submit",
    response_model=ApplicationActionResponse,
)
def submit_application(
    request: SubmitApplicationRequest,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: SubmitApplicationUseCase = Depends(
        get_submit_application_usecase
    ),
):

    # ========================================================
    # REQUEST → DTO
    # ========================================================

    dto = SubmitApplicationDTO(

        # ----------------------------------------------------
        # IDS
        # ----------------------------------------------------

        id=request.id,

        vehicle_id=request.vehicle_id,

        # ----------------------------------------------------
        # TYPE
        # ----------------------------------------------------

        application_type=request.application_type,

        # ----------------------------------------------------
        # USER INFOS
        # ----------------------------------------------------

        first_name=request.first_name,

        last_name=request.last_name,

        email=request.email,

        phone=request.phone,

        address=request.address,

        birth_date=request.birth_date,

        # ----------------------------------------------------
        # RENT
        # ----------------------------------------------------

        selected_dates=(
            SelectedDatesDTO(
                start=request.selected_dates.start,
                end=request.selected_dates.end,
            )
            if request.selected_dates
            else None
        ),

        # ----------------------------------------------------
        # FINANCIAL
        # ----------------------------------------------------

        monthly_income=request.monthly_income,

        monthly_expenses=request.monthly_expenses,

        employment_status=request.employment_status,

        # ----------------------------------------------------
        # OPTIONS
        # ----------------------------------------------------

        selected_option_ids=(
            request.selected_option_ids
        ),

        # ----------------------------------------------------
        # PRICE
        # ----------------------------------------------------

        total_price=request.total_price,

        # ----------------------------------------------------
        # FINANCING
        # ----------------------------------------------------

        financing=(
            FinancingDTO(
                down_payment=(
                    request.financing.down_payment
                ),
                duration_months=(
                    request.financing.duration_months
                ),
            )
            if request.financing
            else None
        ),

        # ----------------------------------------------------
        # TRADE-IN
        # ----------------------------------------------------

        trade_in=(
            TradeInDTO(
                enabled=request.trade_in.enabled,
                brand=request.trade_in.brand,
                model=request.trade_in.model,
                year=request.trade_in.year,
                mileage=request.trade_in.mileage,
                condition=request.trade_in.condition,
            )
            if request.trade_in
            else None
        ),

        # ----------------------------------------------------
        # DOCUMENTS
        # ----------------------------------------------------

        documents=[
            DocumentDTO(
                type=document.type,
                s3_key=document.s3_key,
            )
            for document in request.documents
        ],
    )

    result = usecase.execute(
        dto=dto,
        current_user_id=current_user.id,
    )

    return ApplicationActionResponse(
        id=result.id,
        status=result.status,
        message="Application soumise avec succès.",
    )


# ============================================================
# GET MY APPLICATIONS
# ============================================================

@router.get(
    "/me",
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
    current_user: User = Depends(
        get_current_user
    ),
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
        role=current_user.role,
        user_id=current_user.id,
    )

    return factory.build(
        result=result,
        role=current_user.role,
    )


# ============================================================
# GET APPLICATION BY VEHICLE
# ============================================================

@router.get(
    "/by-vehicle/{vehicle_id}",
    response_model=ApplicationByVehicleResponse | None,
)
def get_application_by_vehicle(
    vehicle_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: GetApplicationByVehicleUseCase = Depends(
        get_application_by_vehicle_usecase
    ),
):
    dto = VehicleIdDTO(
        vehicle_id=vehicle_id
    )
    application = usecase.execute(
        dto=dto,
        current_user_id=current_user.id,
    )

    if application is None:
        return None

    return ApplicationByVehicleResponse(
        id=application.id,
        status=application.status,
    )


# ============================================================
# GET APPLICATION DETAIL
# ============================================================

@router.get(
    "/{application_id}",
    response_model=ApplicationDetailResponse,
)
def get_application(
    application_id: str,

    usecase: GetApplicationUseCase = Depends(
        get_application_usecase
    ),
    factory: ApplicationResponseFactory = Depends(
        get_application_response_factory
    ),
    current_user: User = Depends(
        get_current_user
    ),
):
    dto = ApplicationIdDTO(
    application_id=application_id
)
    application, payment = usecase.execute(
        dto=dto,
        current_user=current_user,
    )

    return factory.build(
        application,
        payment,
    )


# ============================================================
# CANCEL APPLICATION
# ============================================================

@router.patch(
    "/{application_id}/cancel",
    response_model=ApplicationActionResponse,
)
def cancel_application(
    application_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: CancelApplicationUseCase = Depends(
        get_cancel_application_usecase
    ),
):
    dto = ApplicationIdDTO(
        application_id=application_id
    )

    application = usecase.execute(
        dto=dto,
        role=current_user.role,
        user_id=current_user.id,
    )

    return ApplicationActionResponse(
        id=application.id,
        status=application.status,
        message="Application annulée avec succès",
    )


# ============================================================
# DELETE APPLICATION
# ============================================================

@router.delete(
    "/{application_id}",
    response_model=DeleteApplicationResponse,
)
def delete_application(
    application_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    usecase: DeleteApplicationUseCase = Depends(
        get_delete_application_usecase
    ),
):
    dto = ApplicationIdDTO(
        application_id=application_id
    )
    result = usecase.execute(
        dto=dto,
        current_user=current_user,
    )

    return DeleteApplicationResponse(
        id=result.application_id,
        message="Application supprimée définitivement avec succès.",
    )