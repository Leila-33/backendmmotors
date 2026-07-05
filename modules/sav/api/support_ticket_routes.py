from fastapi import APIRouter, Depends, HTTPException
from modules.auth.domain.entities.user import User
from modules.sav.api.schemas import (
    SupportTicketCreate,
    UpdateTicketStatusDTO,
    FindSupportTicketsQuery,
    PaginatedSupportTicketsResponse,
    SupportTicketResponseDTO,
    UnreadTicketCountResponse
)
from modules.sav.application.use_cases.create_support_ticket import CreateSupportTicketUseCase
from modules.sav.application.use_cases.get_support_ticket import GetSupportTicketUseCase
from modules.sav.application.use_cases.find_support_tickets import FindSupportTicketsUseCase
from modules.sav.api.dependencies import (
    get_create_support_ticket_usecase,
    get_find_support_tickets_usecase,
    get_get_support_ticket_usecase
)
from core.security.dependencies import get_current_user
from modules.core.infrastructure.dependencies import get_ticket_repository
from modules.sav.domain.repositories.support_ticket_repository import SupportTicketRepository

router = APIRouter(tags=["Support Tickets"])


# Support tickets

@router.post(
    "",
    response_model=SupportTicketResponseDTO
)
def create_ticket(
    payload: SupportTicketCreate,
    user: User = Depends(get_current_user),
    uc: CreateSupportTicketUseCase = Depends(get_create_support_ticket_usecase),
):
    return uc.execute(
        user_id=user.id,
        user_role=user.role,
        payload=payload
    )

@router.get(
    "/unread-count",
    response_model=UnreadTicketCountResponse,
)
def get_unread_ticket_count(
    user: User = Depends(get_current_user),
    repo: SupportTicketRepository = Depends(get_ticket_repository),
):
    return UnreadTicketCountResponse(
        count=repo.count_unread(user)
    )

@router.get(
    "/{ticket_id}",
    response_model=SupportTicketResponseDTO,
)
async def get_support_ticket(
    ticket_id: str,
    user=Depends(get_current_user),
    uc: GetSupportTicketUseCase = Depends(get_get_support_ticket_usecase),
):
    return await uc.execute(ticket_id, user)


@router.get(
    "",
    response_model=PaginatedSupportTicketsResponse,
)
def get_my_tickets(
    query: FindSupportTicketsQuery = Depends(),
    usecase: FindSupportTicketsUseCase = Depends(
        get_find_support_tickets_usecase
    ),
    current_user: User = Depends(get_current_user),
):
    return usecase.execute(
        query=query,
        user=current_user,
    )






from modules.core.infrastructure.dependencies import get_ticket_read_state_repository
from modules.sav.domain.repositories.ticket_read_state_repository import TicketReadStateRepository
from modules.auth.domain.entities.user import User



