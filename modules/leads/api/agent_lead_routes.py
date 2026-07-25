from fastapi import APIRouter, Depends, Query

from modules.leads.api.schemas import (
    LeadListResponse,
    AssignLeadResponse,
    LeadDetailResponse,
    MarkLeadContactedResponse)
from modules.leads.api.dependencies import (
    get_sales_leads_usecase,
    get_assign_lead_usecase,
    get_lead_detail_usecase,
    get_mark_lead_contacted_usecase,
    get_delete_lead_usecase
)
from core.security.dependencies import get_current_sales_agent
from modules.leads.application.use_cases.agent.get_sales_leads import GetSalesLeadsUseCase
from modules.leads.application.use_cases.agent.assign_lead import AssignLeadUseCase
from modules.leads.application.use_cases.agent.get_lead_detail import GetLeadDetailUseCase
from modules.leads.application.use_cases.agent.mark_lead_contacted import MarkLeadContactedUseCase
from modules.leads.application.use_cases.agent.delete_lead import DeleteLeadUseCase

router = APIRouter(tags=["Agent Leads"])


@router.get("", response_model=list[LeadListResponse])
def get_leads(
      scope: str = Query(
        default="my",
        pattern="^(my|unassigned)$"
    ),
    usecase: GetSalesLeadsUseCase = Depends(
        get_sales_leads_usecase
    ),
    current_user=Depends(get_current_sales_agent)
):

    return usecase.execute(
        scope,
        current_user
    )



@router.patch("/{lead_id}/assign-to-me", response_model=AssignLeadResponse
)
def assign_lead_to_me(
    lead_id: str,
    current_user = Depends(get_current_sales_agent),
    usecase : AssignLeadUseCase = Depends(get_assign_lead_usecase)
):
    return usecase.execute(
        lead_id=lead_id,
        agent_id=current_user.id
    )


@router.get(
    "/{lead_id}",
    response_model=LeadDetailResponse
)
def get_lead_detail(
    lead_id: str,
    current_user = Depends(get_current_sales_agent),
    usecase : GetLeadDetailUseCase = Depends(get_lead_detail_usecase),
):
    return usecase.execute(
        lead_id
    )



@router.patch(
    "/{lead_id}/contact",
    response_model=MarkLeadContactedResponse
)
def mark_lead_contacted(

    lead_id: str,
    current_user = Depends(get_current_sales_agent),
    use_case: MarkLeadContactedUseCase = Depends(
        get_mark_lead_contacted_usecase
    )

):

    return use_case.execute(
        lead_id, current_user.id
    )

@router.delete(
    "/{lead_id}",
    status_code=204,
)
def delete_lead(
    lead_id: str,
    current_user=Depends(
        get_current_sales_agent
    ),
    usecase: DeleteLeadUseCase = Depends(
        get_delete_lead_usecase
    ),
):

    usecase.execute(
        lead_id=lead_id,
        agent_id=current_user.id,
    )