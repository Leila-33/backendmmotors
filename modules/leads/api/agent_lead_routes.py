from fastapi import APIRouter, Depends, Query

from modules.auth.domain.entities.user import User

from core.security.dependencies import get_current_sales_agent

from modules.leads.api.schemas import (
    LeadListResponse,
    AssignLeadResponse,
    LeadDetailResponse,
    MarkLeadContactedResponse,
    DeleteLeadResponse,
)

from modules.leads.api.dependencies import (
    get_get_sales_leads_usecase,
    get_assign_lead_usecase,
    get_get_lead_detail_usecase,
    get_mark_lead_contacted_usecase,
    get_delete_lead_usecase,
)

from modules.leads.application.dtos.agent.get_sales_leads_dto import (
    GetSalesLeadsDTO,
)
from modules.leads.application.dtos.agent.assign_lead_dto import (
    AssignLeadDTO,
)
from modules.leads.application.dtos.agent.get_lead_detail_dto import (
    GetLeadDetailDTO,
)
from modules.leads.application.dtos.agent.mark_lead_contacted_dto import (
    MarkLeadContactedDTO,
)
from modules.leads.application.dtos.agent.delete_lead_dto import (
    DeleteLeadDTO,
)

from modules.leads.application.use_cases.agent.get_sales_leads import (
    GetSalesLeadsUseCase,
)
from modules.leads.application.use_cases.agent.assign_lead import (
    AssignLeadUseCase,
)
from modules.leads.application.use_cases.agent.get_lead_detail import (
    GetLeadDetailUseCase,
)
from modules.leads.application.use_cases.agent.mark_lead_contacted import (
    MarkLeadContactedUseCase,
)
from modules.leads.application.use_cases.agent.delete_lead import (
    DeleteLeadUseCase,
)

from modules.leads.infrastructure.mappers.lead_mapper import (
    LeadMapper,
)


router = APIRouter(
    tags=["Agent Leads"]
)

# ============================================================
# GET SALES LEADS
# ============================================================
@router.get(
    "",
    response_model=LeadListResponse,
)
def get_sales_leads(
    scope: str = Query(
        default="my",
        pattern="^(my|unassigned)$",
    ),
    current_user: User = Depends(
        get_current_sales_agent
    ),
    usecase: GetSalesLeadsUseCase = Depends(
        get_get_sales_leads_usecase
    ),
):
    dto = GetSalesLeadsDTO(
        scope=scope,
        user_id=current_user.id,
    )

    result = usecase.execute(dto)

    return LeadMapper.to_list_response(result)

# ============================================================
# GET LEAD DETAIL
# ============================================================
@router.get(
    "/{lead_id}",
    response_model=LeadDetailResponse,
)
def get_lead_detail(
    lead_id: str,
    current_user: User = Depends(
        get_current_sales_agent
    ),
    usecase: GetLeadDetailUseCase = Depends(
        get_get_lead_detail_usecase
    ),
):
    dto = GetLeadDetailDTO(
        lead_id=lead_id,
    )

    result = usecase.execute(dto)

    return LeadMapper.to_detail_response(result)

# ============================================================
# ASSIGN TO ME
# ============================================================
@router.patch(
    "/{lead_id}/assign-to-me",
    response_model=AssignLeadResponse,
)
def assign_lead(
    lead_id: str,
    current_user: User = Depends(
        get_current_sales_agent
    ),
    usecase: AssignLeadUseCase = Depends(
        get_assign_lead_usecase
    ),
):
    dto = AssignLeadDTO(
        lead_id=lead_id,
        agent_id=current_user.id,
    )

    result = usecase.execute(dto)

    return AssignLeadResponse(
        id=result.id,
        status=result.status,
        assigned_to=result.assigned_to,
        message=result.message,
    )

# ============================================================
# GET LEAD DETAIL
# ============================================================
@router.patch(
    "/{lead_id}/contacted",
    response_model=MarkLeadContactedResponse,
)
def mark_lead_contacted(
    lead_id: str,
    current_user: User = Depends(
        get_current_sales_agent
    ),
    usecase: MarkLeadContactedUseCase = Depends(
        get_mark_lead_contacted_usecase
    ),
):
    dto = MarkLeadContactedDTO(
        lead_id=lead_id,
        agent_id=current_user.id,
    )

    result = usecase.execute(dto)

    return MarkLeadContactedResponse(
        id=result.id,
        status=result.status,
        message=result.message,
    )


# ============================================================
# DELETE LEAD
# ============================================================
@router.delete(
    "/{lead_id}",
    response_model=DeleteLeadResponse,
)
def delete_lead(
    lead_id: str,
    current_user: User = Depends(
        get_current_sales_agent
    ),
    usecase: DeleteLeadUseCase = Depends(
        get_delete_lead_usecase
    ),
):
    dto = DeleteLeadDTO(
        lead_id=lead_id,
        agent_id=current_user.id,
    )

    result = usecase.execute(dto)

    return DeleteLeadResponse(
        id=result.lead_id,
        message=result.message,
    )