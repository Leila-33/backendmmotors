from fastapi import APIRouter, Depends

from modules.auth.domain.entities.user import User

from modules.sav.api.schemas import (
    SavDashboardResponse,
    SavStatisticsResponse,
    CategoryStat,
    SupportTicketResponse,
    UpdateSupportTicketStatusRequest,
)

from modules.sav.api.dependencies import (
    get_get_sav_dashboard_usecase,
    get_get_sav_statistics_usecase,
    get_update_support_ticket_status_usecase,
    get_archive_support_ticket_usecase,
)

from modules.sav.application.dtos.agent.update_support_ticket_status_dto import (
    UpdateSupportTicketStatusDTO,
)

from modules.sav.application.dtos.agent.archive_support_ticket_dto import (
    ArchiveSupportTicketDTO,
)

from modules.sav.application.use_cases.agent.get_sav_dashboard import (
    GetSavDashboardUseCase,
)

from modules.sav.application.use_cases.agent.get_sav_statistics import (
    GetSavStatisticsUseCase,
)

from modules.sav.application.use_cases.agent.update_support_ticket_status import (
    UpdateSupportTicketStatusUseCase,
)

from modules.sav.application.use_cases.agent.archive_support_ticket import (
    ArchiveSupportTicketUseCase,
)

from modules.sav.infrastructure.mappers.support_ticket_mapper import (
    SupportTicketMapper,
)
from modules.sav.infrastructure.mappers.sav_dashboard_mapper import (
    SavDashboardMapper,
)
from core.security.dependencies import get_current_sav_agent


router = APIRouter(
    tags=["Agent Support Tickets"]
)


# =====================================================
# DASHBOARD
# =====================================================

@router.get(
    "/dashboard",
    response_model=SavDashboardResponse,
)
def get_sav_dashboard(
    current_user: User = Depends(
        get_current_sav_agent
    ),
    use_case: GetSavDashboardUseCase = Depends(
        get_get_sav_dashboard_usecase
    ),
):

    result = use_case.execute(current_user.id)

    return SavDashboardMapper.to_response(
        result
    )


# =====================================================
# STATISTICS
# =====================================================

@router.get(
    "/statistics",
    response_model=SavStatisticsResponse,
)
def get_sav_statistics(
    current_user: User = Depends(
        get_current_sav_agent
    ),
    use_case: GetSavStatisticsUseCase = Depends(
        get_get_sav_statistics_usecase
    ),
):

    result = use_case.execute(
        user_id=current_user.id
    )

    return SavStatisticsResponse(
        total=result.total,
        closed=result.closed,
        last_7_days=result.last_7_days,
        last_30_days=result.last_30_days,

        category_distribution=[
            CategoryStat(
                category=item.category,
                count=item.count,
            )
            for item in result.category_distribution
        ],

        resolution_rate=result.resolution_rate,
    )


# =====================================================
# UPDATE STATUS
# =====================================================

@router.patch(
    "/{ticket_id}/status",
    response_model=SupportTicketResponse,
)
async def update_support_ticket_status(
    ticket_id: str,
    payload: UpdateSupportTicketStatusRequest,
    current_user: User = Depends(
        get_current_sav_agent
    ),
    use_case: UpdateSupportTicketStatusUseCase = Depends(
        get_update_support_ticket_status_usecase
    ),
):

    dto = UpdateSupportTicketStatusDTO(
        ticket_id=ticket_id,
        status=payload.status,
        user_id=current_user.id,
    )

    result = await use_case.execute(dto)

    return SupportTicketMapper.to_response(
        result.ticket
    )


# =====================================================
# ARCHIVE
# =====================================================

@router.patch(
    "/{ticket_id}/archive",
    response_model=SupportTicketResponse,
)
def archive_support_ticket(
    ticket_id: str,
    current_user: User = Depends(
        get_current_sav_agent
    ),
    use_case: ArchiveSupportTicketUseCase = Depends(
        get_archive_support_ticket_usecase
    ),
):

    dto = ArchiveSupportTicketDTO(
        ticket_id=ticket_id,
        user_id=current_user.id,
    )

    result = use_case.execute(dto)

    return SupportTicketMapper.to_response(
        result.ticket
    )