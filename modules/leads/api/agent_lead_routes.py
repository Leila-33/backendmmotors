from fastapi import APIRouter, Depends, Query

from modules.auth.domain.entities.user import User

from core.security.dependencies import get_current_sales_agent

from modules.leads.api.schemas import (
    GetSalesLeadsResponse,
    AssignLeadResponse,
    LeadDetailResponse,
    MarkLeadContactedResponse,
    DeleteLeadResponse,
    SalesDashboardStatisticsResponse,
    SalesNotificationCountsResponse
)

from modules.leads.api.dependencies import (
    get_get_sales_leads_usecase,
    get_assign_lead_usecase,
    get_get_lead_detail_usecase,
    get_mark_lead_contacted_usecase,
    get_delete_lead_usecase,
    get_get_sales_dashboard_statistics_usecase,
    get_get_sales_notifications_usecase,
)

from modules.leads.application.dtos.agent.get_sales_leads_dto import (
    GetSalesLeadsDTO,
)
from modules.leads.application.dtos.agent.agent_lead_dto import (
    AgentLeadDTO,
)
from modules.leads.application.dtos.agent.get_lead_detail_dto import (
    GetLeadDetailDTO,
)
from modules.leads.application.dtos.agent.agent_dto import (
    AgentDTO,
)
from modules.leads.application.use_cases.agent.get_sales_dashboard_statistics import (
    GetSalesDashboardStatisticsUseCase,
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
from modules.leads.application.use_cases.agent.get_sales_notifications import (
    GetSalesNotificationsUseCase,
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
    response_model=GetSalesLeadsResponse,
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
# GET SALES DASHBOARD STATISTICS
# ============================================================
@router.get(
    "/stats",
    response_model=SalesDashboardStatisticsResponse,
)
def get_sales_dashboard_statistics(
    current_agent: User = Depends(get_current_sales_agent),
    use_case: GetSalesDashboardStatisticsUseCase = Depends(
        get_get_sales_dashboard_statistics_usecase,
    ),
):

    dto = AgentDTO(
        agent_id=current_agent.id,
    )

    result = use_case.execute(dto)

    return SalesDashboardStatisticsResponse(
        new_leads=result.new_leads,
        my_leads=result.my_leads,
        quotes_sent=result.quotes_sent,
        applications=result.applications,
        unassigned=result.unassigned,
        won=result.won,
        lost=result.lost,
        conversion_rate=result.conversion_rate,
    )

# ============================================================
# GET SALES NOTIFICATIONS
# ============================================================
@router.get(
    "/notifications",
    response_model=SalesNotificationCountsResponse,
)
def get_sales_notifications(
    current_agent: User = Depends(get_current_sales_agent),
    use_case: GetSalesNotificationsUseCase = Depends(
        get_get_sales_notifications_usecase,
    ),
):

    dto = AgentDTO(
        agent_id=current_agent.id,
    )

    result = use_case.execute(dto)

    return SalesNotificationCountsResponse(
        new_leads_count=result.new_leads_count,
        my_leads_count=result.my_leads_count,
    )

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
    dto = AgentLeadDTO(
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
    dto = AgentLeadDTO(
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
    dto = AgentLeadDTO(
        lead_id=lead_id,
        agent_id=current_user.id,
    )

    result = usecase.execute(dto)

    return DeleteLeadResponse(
        id=result.lead_id,
        message=result.message,
    )


