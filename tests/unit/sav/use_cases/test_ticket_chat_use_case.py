from unittest.mock import Mock

import pytest

from modules.auth.domain.enums import UserRole
from modules.sav.application.dtos.create_ticket_message_dto import (
    CreateTicketMessageDTO,
)
from modules.sav.application.use_cases.ticket_chat_use_case import (
    TicketChatUseCase,
)
from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    TicketAccessDenied,
)
from modules.sav.domain.enums import (
    TicketCategory,
    TicketPriority,
    TicketStatus,
)


# ============================================================
# HELPERS
# ============================================================


def make_ticket(
    *,
    ticket_id: str = "ticket-1",
    user_id: str = "user-1",
    assigned_to: str | None = "agent-1",
):
    return SupportTicket(
        id=ticket_id,
        user_id=user_id,
        application_id=None,
        subject="Problème véhicule",
        description="Description du problème",
        category=TicketCategory.VEHICLE_ISSUE,
        status=TicketStatus.OPEN,
        priority=TicketPriority.MEDIUM,
        assigned_to=assigned_to,
    )


def make_message_dto(
    *,
    ticket_id: str = "ticket-1",
    message: str = "Bonjour, j'ai une question.",
):
    return CreateTicketMessageDTO(
        ticket_id=ticket_id,
        message=message,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def ticket_repository():
    return Mock()


@pytest.fixture
def create_message_uc():
    return Mock()


@pytest.fixture
def chat_manager():
    return Mock()


@pytest.fixture
def connection_manager():
    return Mock()


@pytest.fixture
def use_case(
    ticket_repository,
    create_message_uc,
    chat_manager,
    connection_manager,
):
    return TicketChatUseCase(
        ticket_repository=ticket_repository,
        create_message_uc=create_message_uc,
        chat_manager=chat_manager,
        connection_manager=connection_manager,
    )


@pytest.fixture
def ticket():
    return make_ticket()


@pytest.fixture
def dto():
    return make_message_dto()


# ============================================================
# CHECK ACCESS
# ============================================================


def test_check_access_ticket_not_found(
    use_case,
    ticket_repository,
):
    ticket_repository.get_by_id.return_value = None

    with pytest.raises(SupportTicketNotFound):
        use_case.check_access(
            ticket_id="ticket-1",
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    ticket_repository.get_by_id.assert_called_once_with(
        "ticket-1"
    )


def test_check_access_owner_can_access_ticket(
    use_case,
    ticket_repository,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    result = use_case.check_access(
        ticket_id="ticket-1",
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert result is ticket

    ticket_repository.get_by_id.assert_called_once_with(
        "ticket-1"
    )


def test_check_access_admin_can_access_any_ticket(
    use_case,
    ticket_repository,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    result = use_case.check_access(
        ticket_id="ticket-1",
        user_id="another-user",
        user_role=UserRole.ADMIN,
    )

    assert result is ticket

    ticket_repository.get_by_id.assert_called_once_with(
        "ticket-1"
    )


def test_check_access_sav_agent_can_access_any_ticket(
    use_case,
    ticket_repository,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    result = use_case.check_access(
        ticket_id="ticket-1",
        user_id="another-user",
        user_role=UserRole.SAV_AGENT,
    )

    assert result is ticket

    ticket_repository.get_by_id.assert_called_once_with(
        "ticket-1"
    )


def test_check_access_other_client_is_denied(
    use_case,
    ticket_repository,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(TicketAccessDenied):
        use_case.check_access(
            ticket_id="ticket-1",
            user_id="another-user",
            user_role=UserRole.CLIENT,
        )

    ticket_repository.get_by_id.assert_called_once_with(
        "ticket-1"
    )


# ============================================================
# SEND MESSAGE
# ============================================================


def test_send_message_checks_access(
    use_case,
    ticket_repository,
    create_message_uc,
    dto,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    message = Mock(
        id="message-1",
        ticket_id="ticket-1",
    )

    create_message_uc.execute.return_value = Mock(
        message=message
    )

    returned_ticket, returned_message = use_case.send_message(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert returned_ticket is ticket
    assert returned_message is message

    ticket_repository.get_by_id.assert_called_once_with(
        "ticket-1"
    )


def test_send_message_delegates_to_create_message_use_case(
    use_case,
    ticket_repository,
    create_message_uc,
    dto,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    message = Mock(
        id="message-1",
        ticket_id="ticket-1",
    )

    create_message_uc.execute.return_value = Mock(
        message=message
    )

    use_case.send_message(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    create_message_uc.execute.assert_called_once_with(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )


def test_send_message_returns_ticket_and_created_message(
    use_case,
    ticket_repository,
    create_message_uc,
    dto,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    message = Mock(
        id="message-1",
        ticket_id="ticket-1",
    )

    create_message_uc.execute.return_value = Mock(
        message=message
    )

    returned_ticket, returned_message = use_case.send_message(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert returned_ticket is ticket
    assert returned_message is message


def test_send_message_is_denied_before_creating_message(
    use_case,
    ticket_repository,
    create_message_uc,
    dto,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(TicketAccessDenied):
        use_case.send_message(
            dto=dto,
            user_id="another-user",
            user_role=UserRole.CLIENT,
        )

    create_message_uc.execute.assert_not_called()


def test_send_message_admin_can_send_to_any_ticket(
    use_case,
    ticket_repository,
    create_message_uc,
    dto,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    message = Mock(
        id="message-1",
        ticket_id="ticket-1",
    )

    create_message_uc.execute.return_value = Mock(
        message=message
    )

    returned_ticket, returned_message = use_case.send_message(
        dto=dto,
        user_id="admin-1",
        user_role=UserRole.ADMIN,
    )

    assert returned_ticket is ticket
    assert returned_message is message

    create_message_uc.execute.assert_called_once_with(
        dto=dto,
        user_id="admin-1",
        user_role=UserRole.ADMIN,
    )


def test_send_message_sav_agent_can_send_to_any_ticket(
    use_case,
    ticket_repository,
    create_message_uc,
    dto,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    message = Mock(
        id="message-1",
        ticket_id="ticket-1",
    )

    create_message_uc.execute.return_value = Mock(
        message=message
    )

    returned_ticket, returned_message = use_case.send_message(
        dto=dto,
        user_id="agent-1",
        user_role=UserRole.SAV_AGENT,
    )

    assert returned_ticket is ticket
    assert returned_message is message

    create_message_uc.execute.assert_called_once_with(
        dto=dto,
        user_id="agent-1",
        user_role=UserRole.SAV_AGENT,
    )


def test_send_message_propagates_create_message_error(
    use_case,
    ticket_repository,
    create_message_uc,
    dto,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    create_message_uc.execute.side_effect = RuntimeError(
        "message creation error"
    )

    with pytest.raises(
        RuntimeError,
        match="message creation error",
    ):
        use_case.send_message(
            dto=dto,
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )


# ============================================================
# GET RECIPIENT — CLIENT
# ============================================================


def test_get_recipient_returns_assigned_agent_for_client_message(
    use_case,
    ticket,
):
    ticket.assigned_to = "agent-1"

    recipient = use_case.get_recipient(
        ticket=ticket,
        sender_id="user-1",
    )

    assert recipient == (
        "agent-1",
        UserRole.SAV_AGENT,
    )


def test_get_recipient_returns_none_when_client_has_no_agent(
    use_case,
    ticket,
):
    ticket.assigned_to = None

    recipient = use_case.get_recipient(
        ticket=ticket,
        sender_id="user-1",
    )

    assert recipient is None


# ============================================================
# GET RECIPIENT — SAV AGENT
# ============================================================


def test_get_recipient_returns_client_for_agent_message(
    use_case,
    ticket,
):
    recipient = use_case.get_recipient(
        ticket=ticket,
        sender_id="agent-1",
    )

    assert recipient == (
        "user-1",
        UserRole.CLIENT,
    )


def test_get_recipient_returns_ticket_owner_for_any_non_owner_sender(
    use_case,
    ticket,
):
    recipient = use_case.get_recipient(
        ticket=ticket,
        sender_id="another-agent",
    )

    assert recipient == (
        "user-1",
        UserRole.CLIENT,
    )


# ============================================================
# NO UNEXPECTED SIDE EFFECTS
# ============================================================


def test_check_access_does_not_modify_ticket(
    use_case,
    ticket_repository,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    original_assigned_to = ticket.assigned_to
    original_status = ticket.status

    use_case.check_access(
        ticket_id="ticket-1",
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert ticket.assigned_to == original_assigned_to
    assert ticket.status == original_status


def test_get_recipient_does_not_modify_ticket(
    use_case,
    ticket,
):
    original_assigned_to = ticket.assigned_to

    use_case.get_recipient(
        ticket=ticket,
        sender_id="user-1",
    )

    assert ticket.assigned_to == original_assigned_to