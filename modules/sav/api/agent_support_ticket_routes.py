from fastapi import APIRouter, Depends

from modules.sav.api.schemas import (
    SavDashboardResponse,
    SavStatisticsResponse,
    SupportTicketResponseDTO,
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
    response_model=SupportTicketResponseDTO,
)
async def update_ticket_status(
    ticket_id: str,
    payload: UpdateTicketStatusDTO,
    user=Depends(get_current_sav_agent),
    uc: UpdateSupportTicketStatusUseCase = Depends(
        get_update_support_ticket_status_usecase
    ),
):
    return await uc.execute(ticket_id, payload.status, user)

@router.patch("/{ticket_id}/archive")
def archive_ticket(
    ticket_id: str,
    user=Depends(get_current_sav_agent),
    uc: ArchiveSupportTicketUseCase = Depends(get_archive_support_ticket_usecase)
):
    return uc.execute(ticket_id, user)