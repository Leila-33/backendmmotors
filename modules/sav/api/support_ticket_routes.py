from fastapi import APIRouter, Depends, status
from modules.auth.domain.entities.user import User
from modules.sav.api.schemas import (
    CreateSupportTicketRequest,
    FindSupportTicketsQuery,
    PaginatedSupportTicketsResponse,
    SupportTicketResponse,
    UnreadTicketCountResponse,
)
from modules.auth.domain.entities.user import User
from modules.sav.application.use_cases.create_support_ticket import CreateSupportTicketUseCase
from modules.sav.application.use_cases.get_support_ticket import GetSupportTicketUseCase
from modules.sav.application.use_cases.find_support_tickets import FindSupportTicketsUseCase
from modules.sav.api.dependencies import (
    get_create_support_ticket_usecase,
    get_find_support_tickets_usecase,
    get_get_support_ticket_usecase,
)
from core.security.dependencies import get_current_user
from modules.dependencies.dependencies import get_ticket_repository
from modules.sav.domain.repositories.support_ticket_repository import SupportTicketRepository
from modules.sav.infrastructure.mappers.support_ticket_mapper import SupportTicketMapper

router = APIRouter(tags=["Support Tickets"])


@router.post(
    "",
    response_model=SupportTicketResponse,
    status_code=status.HTTP_201_CREATED
)
def create_ticket(
    payload: CreateSupportTicketRequest,
    current_user=Depends(get_current_user),
    use_case=Depends(get_create_support_ticket_usecase)
):

    ticket = use_case.execute(
        user_id=current_user.id,
        user_role=current_user.role,
        payload=payload
    )

    return SupportTicketMapper.to_response(ticket)


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
    response_model=SupportTicketResponse
)
async def get_ticket(
    ticket_id: str,
    current_user=Depends(get_current_user),
    use_case=Depends(get_get_support_ticket_usecase)
):

    ticket = await use_case.execute(
        ticket_id,
        current_user
    )

    return SupportTicketMapper.to_response(ticket)


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




