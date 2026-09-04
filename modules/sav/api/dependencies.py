from fastapi import Depends

# =========================================================
# CLIENT USE CASES
# =========================================================

from modules.sav.application.use_cases.create_support_ticket import (
    CreateSupportTicketUseCase,
)

from modules.sav.application.use_cases.get_support_ticket import (
    GetSupportTicketUseCase,
)

from modules.sav.application.use_cases.find_support_tickets import (
    FindSupportTicketsUseCase,
)

from modules.sav.application.use_cases.create_ticket_message import (
    CreateTicketMessageUseCase,
)

from modules.sav.application.use_cases.get_unread_ticket_count import (
    GetUnreadTicketCountUseCase,
)

from modules.sav.application.use_cases.ticket_chat_use_case import (
    TicketChatUseCase,
)


# =========================================================
# AGENT USE CASES
# =========================================================

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


# =========================================================
# SERVICES
# =========================================================

from modules.sav.application.services.assignment_service import (
    AssignmentService,
)


# =========================================================
# DATABASE
# =========================================================

from core.database.dependencies import (
    get_unit_of_work,
)


# =========================================================
# APPLICATION SERVICES
# =========================================================

from modules.dependencies.dependencies import (
    get_user_repository,
    get_ticket_repository,
    get_ticket_message_repository,
    get_ticket_read_state_repository,
    get_ticket_chat_manager,
    get_websocket_manager,
    get_event_service,
)


# =========================================================
# ASSIGNMENT SERVICE
# =========================================================

def get_assignment_service(
    user_repository=Depends(
        get_user_repository
    ),
    ticket_repository=Depends(
        get_ticket_repository
    ),
):

    return AssignmentService(
        user_repository=user_repository,
        ticket_repository=ticket_repository,
    )


# =========================================================
# CREATE SUPPORT TICKET
# =========================================================

def get_create_support_ticket_usecase(
    ticket_repository=Depends(
        get_ticket_repository
    ),
    message_repository=Depends(
        get_ticket_message_repository
    ),
    assignment_service=Depends(
        get_assignment_service
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):

    return CreateSupportTicketUseCase(
        ticket_repository=ticket_repository,
        message_repository=message_repository,
        assignment_service=assignment_service,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# =========================================================
# GET SUPPORT TICKET
# =========================================================

def get_get_support_ticket_usecase(
    ticket_repository=Depends(
        get_ticket_repository
    ),
    read_state_repository=Depends(
        get_ticket_read_state_repository
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):

    return GetSupportTicketUseCase(
        ticket_repository=ticket_repository,
        read_state_repository=read_state_repository,
        unit_of_work=unit_of_work,
    )


# =========================================================
# UNREAD TICKET COUNT
# =========================================================

def get_unread_ticket_count_usecase(
    ticket_repository=Depends(
        get_ticket_repository
    ),
):

    return GetUnreadTicketCountUseCase(
        support_ticket_repository=ticket_repository,
    )


# =========================================================
# FIND SUPPORT TICKETS
# =========================================================

def get_find_support_tickets_usecase(
    ticket_repository=Depends(
        get_ticket_repository
    ),
):

    return FindSupportTicketsUseCase(
        ticket_repository
    )


# =========================================================
# CREATE TICKET MESSAGE
# =========================================================

def get_create_ticket_message_usecase(
    ticket_repository=Depends(
        get_ticket_repository
    ),
    message_repository=Depends(
        get_ticket_message_repository
    ),
    read_state_repository=Depends(
        get_ticket_read_state_repository
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):

    return CreateTicketMessageUseCase(
        ticket_repository=ticket_repository,
        message_repository=message_repository,
        read_state_repository=read_state_repository,
        unit_of_work=unit_of_work,
    )


# =========================================================
# TICKET CHAT
# =========================================================

def get_ticket_chat_usecase(
    create_message_usecase: CreateTicketMessageUseCase = Depends(
        get_create_ticket_message_usecase
    ),
    ticket_chat_manager=Depends(
        get_ticket_chat_manager
    ),
    websocket_manager=Depends(
        get_websocket_manager
    ),
    ticket_repository=Depends(
        get_ticket_repository
    ),
):

    return TicketChatUseCase(
        chat_manager=ticket_chat_manager,
        connection_manager=websocket_manager,
        ticket_repository=ticket_repository,
        create_message_uc=create_message_usecase,
    )


# =========================================================
# SAV DASHBOARD
# =========================================================

def get_get_sav_dashboard_usecase(
    ticket_repository=Depends(
        get_ticket_repository
    ),
):

    return GetSavDashboardUseCase(
        ticket_repository
    )


# =========================================================
# SAV STATISTICS
# =========================================================

def get_get_sav_statistics_usecase(
    ticket_repository=Depends(
        get_ticket_repository
    ),
):

    return GetSavStatisticsUseCase(
        ticket_repository
    )


# =========================================================
# UPDATE SUPPORT TICKET STATUS
# =========================================================

def get_update_support_ticket_status_usecase(
    ticket_repository=Depends(
        get_ticket_repository
    ),
    chat_manager=Depends(
        get_ticket_chat_manager
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):

    return UpdateSupportTicketStatusUseCase(
        repo=ticket_repository,
        chat_manager=chat_manager,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# =========================================================
# ARCHIVE SUPPORT TICKET
# =========================================================

def get_archive_support_ticket_usecase(
    ticket_repository=Depends(
        get_ticket_repository
    ),
    event_service=Depends(
        get_event_service
    ),
    unit_of_work=Depends(
        get_unit_of_work
    ),
):

    return ArchiveSupportTicketUseCase(
        support_ticket_repository=ticket_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )