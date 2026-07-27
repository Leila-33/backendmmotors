from fastapi import APIRouter, Depends

from modules.sav.api.schemas import (
    SavDashboardResponse,
    SavStatisticsResponse,
    SupportTicketResponse,
    UpdateTicketStatusDTO
)

from modules.sav.api.dependencies import (
    get_get_sav_dashboard_usecase,
    get_get_sav_statistics_usecase,
    get_update_support_ticket_status_usecase,
    get_archive_support_ticket_usecase
)
from modules.sav.application.use_cases.agent.get_sav_dashboard import GetSavDashboardUseCase
from modules.sav.application.use_cases.agent.get_sav_statistics import GetSavStatisticsUseCase
from modules.sav.application.use_cases.agent.update_support_ticket_status import UpdateSupportTicketStatusUseCase
from modules.sav.application.use_cases.agent.archive_support_ticket import ArchiveSupportTicketUseCase
from core.security.dependencies import get_current_sav_agent
from modules.sav.infrastructure.mappers.support_ticket_mapper import SupportTicketMapper

router = APIRouter(tags=["Agent Support Tickets"])




@router.get("/dashboard", response_model=SavDashboardResponse)
def get_sav_dashboard(
    agent=Depends(get_current_sav_agent),
    usecase: GetSavDashboardUseCase = Depends(get_get_sav_dashboard_usecase)
):

    return usecase.execute(agent)



@router.get("/statistics", response_model=SavStatisticsResponse)
def get_sav_statistics(
    agent=Depends(get_current_sav_agent),
    usecase: GetSavStatisticsUseCase = Depends(get_get_sav_statistics_usecase),
):

    return usecase.execute(agent)



@router.patch(
    "/{ticket_id}/status",
    response_model=SupportTicketResponse,
)
async def update_ticket_status(
    ticket_id: str,
    payload: UpdateTicketStatusDTO,
    user=Depends(get_current_sav_agent),
    uc: UpdateSupportTicketStatusUseCase = Depends(
        get_update_support_ticket_status_usecase
    ),
):

    ticket = await uc.execute(
        ticket_id=ticket_id,
        status=payload.status,
        user=user
    )

    return SupportTicketMapper.to_response(ticket)


@router.patch("/{ticket_id}/archive")
def archive_ticket(
    ticket_id: str,
    user=Depends(get_current_sav_agent),
    uc: ArchiveSupportTicketUseCase = Depends(get_archive_support_ticket_usecase)
):
    return uc.execute(ticket_id, user)