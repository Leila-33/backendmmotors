from fastapi import APIRouter, Depends, status

from modules.auth.domain.entities.user import User

from modules.leads.api.schemas import (
    CreateLeadRequest,
    CreateLeadResponse,
)
from modules.dependencies.dependencies import (
    get_sales_dashboard_repository,
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
from modules.auth.domain.enums import UserRole
from core.security.dependencies import (
    get_optional_current_user,
    get_user_repository
)
from modules.notifications.api.dependencies import (
    get_notification_service,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Leads"])


@router.post(
    "",
    response_model=CreateLeadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead(
    request: CreateLeadRequest,
    current_user: User | None = Depends(
        get_optional_current_user
    ),
    usecase: CreateLeadUseCase = Depends(
        get_create_lead_usecase
    ),
    sales_dashboard_repository=Depends(get_sales_dashboard_repository),
    user_repository=Depends(get_user_repository),
    notification_service=Depends(get_notification_service),

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
    # Mettre à jour le compteur des nouveaux leads non attribués
    try:
        count = sales_dashboard_repository.count_new_leads()

        sales_agents = (
                user_repository.get_by_role(
                    UserRole.SALES_AGENT,
                )
            )

        for agent in sales_agents:
                await notification_service.send_update(
                    user_id=str(agent.id),
                    payload={
                        "type": "NEW_LEADS_UPDATED",
                        "count": count,
                    },
                )

    except Exception:
        logger.exception(
            "Erreur lors de la mise à jour du compteur des nouveaux leads"
        )
    return CreateLeadResponse(
        lead_id=result.lead_id,
        status=result.status,
        message=result.message,
    )