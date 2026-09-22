from fastapi import APIRouter, Depends, status

from core.security.dependencies import get_current_user

from modules.auth.domain.entities.user import User

from modules.sav.api.schemas import (
    CreateSupportTicketRequest,
    FindSupportTicketsQuery,
    SupportTicketListItemResponse,
    SupportTicketResponse,
    UnreadTicketCountResponse,
)

from modules.sav.application.dtos.create_support_ticket_dto import (
    CreateSupportTicketDTO,
)

from modules.sav.application.dtos.find_support_tickets_dto import (
    FindSupportTicketsDTO,
)

from modules.sav.application.dtos.get_support_ticket_dto import (
    GetSupportTicketDTO,
)

from modules.sav.application.use_cases.create_support_ticket import (
    CreateSupportTicketUseCase,
)

from modules.sav.application.use_cases.find_support_tickets import (
    FindSupportTicketsUseCase,
)

from modules.sav.application.use_cases.get_support_ticket import (
    GetSupportTicketUseCase,
)

from modules.sav.application.use_cases.get_unread_ticket_count import (
    GetUnreadTicketCountUseCase,
)

from modules.sav.api.dependencies import (
    get_create_support_ticket_usecase,
    get_find_support_tickets_usecase,
    get_get_support_ticket_usecase,
    get_unread_ticket_count_usecase,
    get_websocket_manager,
)

from modules.sav.infrastructure.mappers.support_ticket_mapper import (
    SupportTicketMapper,
)
from core.pagination.paginated_response import PaginatedResponse

router = APIRouter(
    tags=["Support Tickets"]
)


# =====================================================
# CREATE TICKET
# =====================================================

@router.post(
    "",
    response_model=SupportTicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    payload: CreateSupportTicketRequest,
    current_user: User = Depends(get_current_user),
    use_case: CreateSupportTicketUseCase = Depends(
        get_create_support_ticket_usecase
    ),
):

    dto = CreateSupportTicketDTO(
        subject=payload.subject,
        category=payload.category,
        message=payload.message,
        priority=payload.priority,
        application_id=payload.application_id,
    )

    result = use_case.execute(
        dto=dto,
        user_id=current_user.id,
        user_role=current_user.role,
    )

    return SupportTicketMapper.to_response(
        result.ticket
    )


# =====================================================
# UNREAD COUNT
# =====================================================

@router.get(
    "/unread-count",
    response_model=UnreadTicketCountResponse,
)
async def get_unread_ticket_count(
    current_user: User = Depends(get_current_user),

    use_case: GetUnreadTicketCountUseCase = Depends(
        get_unread_ticket_count_usecase
    ),

    connection_manager=Depends(
        get_websocket_manager
    ),
):

    result = use_case.execute(
        user_id=current_user.id,
        user_role=current_user.role,
    )

    # Notification WS éventuelle
    await connection_manager.send(
        current_user.id,
        {
            "type": "UNREAD_TICKETS_UPDATED",
            "count": result.count,
        },
    )

    return UnreadTicketCountResponse(
        count=result.count
    )


# =====================================================
# FIND TICKETS
# =====================================================

@router.get(
    "",
    response_model=PaginatedResponse[SupportTicketListItemResponse],
)
def find_support_tickets(
    query: FindSupportTicketsQuery = Depends(),

    current_user: User = Depends(
        get_current_user
    ),

    use_case: FindSupportTicketsUseCase = Depends(
        get_find_support_tickets_usecase
    ),
):

    # =====================================
    # API → APPLICATION DTO
    # =====================================

    dto = FindSupportTicketsDTO(
        page=query.page,
        limit=query.limit,
        search=query.search,
        status=query.status,
        priority=query.priority,
        category=query.category,
        sort=query.sort,
        filter=query.filter,
        archive=query.archive,
    )

    # =====================================
    # USE CASE
    # =====================================

    result = use_case.execute(
        dto=dto,
        user_id=current_user.id,
        user_role=current_user.role,
    )

    # =====================================
    # RESULT → API RESPONSE
    # =====================================

    return SupportTicketMapper.to_paginated_response(
        result
    )


# =====================================================
# GET TICKET
# =====================================================

@router.get(
    "/{ticket_id}",
    response_model=SupportTicketResponse,
)
async def get_support_ticket(
    ticket_id: str,

    current_user: User = Depends(
        get_current_user
    ),

    use_case: GetSupportTicketUseCase = Depends(
        get_get_support_ticket_usecase
    ),

    connection_manager=Depends(
        get_websocket_manager
    ),
):

    # =====================================
    # API → APPLICATION DTO
    # =====================================

    dto = GetSupportTicketDTO(
        ticket_id=ticket_id,
        user_id=current_user.id,
        user_role=current_user.role,
    )

    # =====================================
    # USE CASE
    # =====================================

    result = use_case.execute(dto)

    # =====================================
    # WEBSOCKET NOTIFICATION
    # =====================================

    await connection_manager.send(
        current_user.id,
        {
            "type": "UNREAD_TICKETS_UPDATED",
            "count": result.unread_count,
        },
    )

    # =====================================
    # RESULT → API RESPONSE
    # =====================================

    return SupportTicketMapper.to_response(
        result.ticket
    )