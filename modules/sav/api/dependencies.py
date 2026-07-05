from fastapi import Depends

from modules.sav.application.use_cases.create_support_ticket import CreateSupportTicketUseCase
from modules.sav.application.use_cases.get_support_ticket import GetSupportTicketUseCase
from modules.sav.application.use_cases.agent.update_support_ticket_status import UpdateSupportTicketStatusUseCase
from modules.sav.application.use_cases.find_support_tickets import FindSupportTicketsUseCase
from modules.sav.application.use_cases.create_ticket_message import CreateTicketMessageUseCase
from modules.sav.application.services.assignment_service import AssignmentService
from modules.sav.application.use_cases.ticket_chat_use_case import TicketChatUseCase
from modules.sav.application.use_cases.agent.get_sav_dashboard import GetSavDashboardUseCase
from modules.sav.application.use_cases.agent.get_sav_statistics import GetSavStatisticsUseCase
from modules.sav.application.use_cases.agent.archive_support_ticket import ArchiveSupportTicketUseCase
from core.dependencies import get_jwt_service
from fastapi import Depends

from modules.sav.application.use_cases.admin.get_open_ticket_count import (
    GetOpenTicketCountUseCase,
)
    

from modules.core.infrastructure.dependencies import (
    get_user_repository,
    get_ticket_repository,
    get_blacklist_repository,
    get_ticket_message_repository,
    get_ticket_read_state_repository,
    get_ticket_chat_manager,
    get_websocket_manager
)

def get_assignment_service(
    user_repo = Depends(get_user_repository),
    ticket_repo = Depends(get_ticket_repository)
):
    return AssignmentService(
        user_repo=user_repo,
        ticket_repo=ticket_repo
    )

def get_create_support_ticket_usecase(
    ticket_repo = Depends(get_ticket_repository),
    message_repo = Depends(get_ticket_message_repository),
    assignment_service = Depends(get_assignment_service)
):
    return CreateSupportTicketUseCase(
        repo=ticket_repo,
        message_repo=message_repo,
        assignment_service=assignment_service
    )

def get_get_support_ticket_usecase(
    repo=Depends(get_ticket_repository),
    read_state_repo=Depends(get_ticket_read_state_repository),
    websocket_manager = Depends(get_websocket_manager),
):
    return GetSupportTicketUseCase(
        repo=repo,
        read_state_repo=read_state_repo,
        connection_manager=websocket_manager,
        )

def get_update_support_ticket_status_usecase(
    repo=Depends(get_ticket_repository),
    chat_manager=Depends(get_ticket_chat_manager)
):
    return UpdateSupportTicketStatusUseCase(
        repo=repo,
        chat_manager=chat_manager
        )


def get_find_support_tickets_usecase(
    repo=Depends(get_ticket_repository)
):
    return FindSupportTicketsUseCase(repo)





def get_create_ticket_message_usecase(
    ticket_repo = Depends(get_ticket_repository),
    message_repo = Depends(get_ticket_message_repository),
    read_state_repo = Depends(get_ticket_read_state_repository)
) -> CreateTicketMessageUseCase:

    return CreateTicketMessageUseCase(
        ticket_repo=ticket_repo,
        message_repo=message_repo,
        read_state_repo=read_state_repo
    )







def get_ticket_chat_usecase(
    create_message_uc: CreateTicketMessageUseCase = Depends(get_create_ticket_message_usecase),
    ticket_chat_manager = Depends(get_ticket_chat_manager),
    websocket_manager = Depends(get_websocket_manager),
    jwt_service = Depends(get_jwt_service),
    user_repo = Depends(get_user_repository),
    blacklist_repo = Depends(get_blacklist_repository),
    ticket_repo = Depends(get_ticket_repository),
    read_state_repo = Depends(get_ticket_read_state_repository)
):

    return TicketChatUseCase(
        manager=ticket_chat_manager,
        connection_manager=websocket_manager,
        jwt_service=jwt_service,
        user_repo=user_repo,
        blacklist_repo=blacklist_repo,
        ticket_repo=ticket_repo,
        create_message_uc=create_message_uc,
        read_state_repo=read_state_repo
    )



def get_open_ticket_count_usecase(
    repo=Depends(get_ticket_repository),
):
    return GetOpenTicketCountUseCase(repo)


def get_get_sav_dashboard_usecase(
    repo=Depends(get_ticket_repository),
):
    return GetSavDashboardUseCase(repo)

def get_get_sav_statistics_usecase(
    repo=Depends(get_ticket_repository),
):
    return GetSavStatisticsUseCase(repo)

def get_archive_support_ticket_usecase(
    repo=Depends(get_ticket_repository),
):
    return ArchiveSupportTicketUseCase(repo)

