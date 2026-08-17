from fastapi import APIRouter, Depends, status

from modules.auth.domain.entities.user import User

from modules.leads.api.schemas import (
    CreateLeadRequest,
    CreateLeadResponse,
)

from modules.leads.api.dependencies import (
    get_create_lead_usecase,
)

from modules.leads.application.dtos.create_lead_dto import (
    CreateLeadDTO,
)

from modules.leads.application.use_cases.create_lead import (
    CreateLeadUseCase,
)

from core.security.dependencies import (
    get_optional_current_user,
)


router = APIRouter(tags=["Leads"])


@router.post(
    "",
    response_model=CreateLeadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(
    request: CreateLeadRequest,
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    usecase: CreateLeadUseCase = Depends(
        get_create_lead_usecase
    ),
):

    dto = CreateLeadDTO(
        vehicle_id=request.vehicle_id,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone=request.phone,
        message=request.message,
        user_id=(
            current_user.id
            if current_user
            else None
        ),
    )

    result = usecase.execute(dto)

    return CreateLeadResponse(
        lead_id=result.lead_id,
        status=result.status,
        message=result.message,
    )