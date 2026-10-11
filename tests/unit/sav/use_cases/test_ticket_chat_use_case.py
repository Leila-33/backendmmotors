from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

from modules.auth.domain.enums import UserRole
from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    TicketAccessDenied,
)
from modules.sav.application.use_cases.ticket_chat_use_case import (
    TicketChatUseCase,
)


@pytest.fixture
def ticket_repository():
    return MagicMock()


@pytest.fixture
def create_message_uc():
    return MagicMock()


@pytest.fixture
def chat_manager():
    return MagicMock()


@pytest.fixture
def read_state_repository():
    return MagicMock()


@pytest.fixture
def unit_of_work():
    return MagicMock()


@pytest.fixture
def use_case(
    ticket_repository,
    create_message_uc,
    chat_manager,
    read_state_repository,
    unit_of_work,
):
    return TicketChatUseCase(
        ticket_repository=ticket_repository,
        create_message_uc=create_message_uc,
        chat_manager=chat_manager,
        read_state_repository=read_state_repository,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def ticket():
    return SimpleNamespace(
        id="ticket-123",
        user_id="client-123",
        assigned_to="agent-456",
    )


@pytest.fixture
def message_dto():
    return SimpleNamespace(
        ticket_id="ticket-123",
        content="Bonjour, j'ai besoin d'aide.",
    )


# =========================================================
# CHECK ACCESS
# =========================================================

def test_check_access_returns_ticket_for_owner(
    use_case,
    ticket_repository,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    result = use_case.check_access(
        ticket_id="ticket-123",
        user_id="client-123",
        user_role=UserRole.CLIENT,
    )

    assert result is ticket
    ticket_repository.get_by_id.assert_called_once_with("ticket-123")


def test_check_access_raises_when_ticket_does_not_exist(
    use_case,
    ticket_repository,
):
    ticket_repository.get_by_id.return_value = None

    with pytest.raises(SupportTicketNotFound):
        use_case.check_access(
            ticket_id="ticket-123",
            user_id="client-123",
            user_role=UserRole.CLIENT,
        )

    ticket_repository.get_by_id.assert_called_once_with("ticket-123")


def test_check_access_denies_another_client(
    use_case,
    ticket_repository,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(TicketAccessDenied):
        use_case.check_access(
            ticket_id="ticket-123",
            user_id="another-client",
            user_role=UserRole.CLIENT,
        )


@pytest.mark.parametrize(
    "role",
    [
        UserRole.ADMIN,
        UserRole.SAV_AGENT,
    ],
)
def test_check_access_allows_admin_and_sav_agent(
    use_case,
    ticket_repository,
    ticket,
    role,
):
    ticket_repository.get_by_id.return_value = ticket

    result = use_case.check_access(
        ticket_id="ticket-123",
        user_id="another-user",
        user_role=role,
    )

    assert result is ticket


# =========================================================
# SEND MESSAGE
# =========================================================

def test_send_message_returns_ticket_and_created_message(
    use_case,
    ticket_repository,
    create_message_uc,
    ticket,
    message_dto,
):
    created_message = SimpleNamespace(
        id="message-123",
        message="Bonjour, j'ai besoin d'aide.",
    )
    create_message_uc.execute.return_value = created_message
    ticket_repository.get_by_id.return_value = ticket

    result_ticket, result_message = use_case.send_message(
        dto=message_dto,
        user_id="client-123",
        user_role=UserRole.CLIENT,
    )

    assert result_ticket is ticket
    assert result_message == "Bonjour, j'ai besoin d'aide."

    ticket_repository.get_by_id.assert_called_once_with("ticket-123")
    create_message_uc.execute.assert_called_once_with(
        dto=message_dto,
        user_id="client-123",
        user_role=UserRole.CLIENT,
    )


def test_send_message_checks_access_before_creating_message(
    use_case,
    ticket_repository,
    create_message_uc,
    ticket,
    message_dto,
):
    ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(TicketAccessDenied):
        use_case.send_message(
            dto=message_dto,
            user_id="another-client",
            user_role=UserRole.CLIENT,
        )

    create_message_uc.execute.assert_not_called()


def test_send_message_raises_if_ticket_does_not_exist(
    use_case,
    ticket_repository,
    create_message_uc,
    message_dto,
):
    ticket_repository.get_by_id.return_value = None

    with pytest.raises(SupportTicketNotFound):
        use_case.send_message(
            dto=message_dto,
            user_id="client-123",
            user_role=UserRole.CLIENT,
        )

    create_message_uc.execute.assert_not_called()


def test_send_message_propagates_creation_error(
    use_case,
    ticket_repository,
    create_message_uc,
    ticket,
    message_dto,
):
    ticket_repository.get_by_id.return_value = ticket
    create_message_uc.execute.side_effect = RuntimeError("Erreur de création")

    with pytest.raises(RuntimeError, match="Erreur de création"):
        use_case.send_message(
            dto=message_dto,
            user_id="client-123",
            user_role=UserRole.CLIENT,
        )


# =========================================================
# GET RECIPIENT
# =========================================================

def test_get_recipient_returns_assigned_agent_for_client_message(
    use_case,
    ticket,
):
    result = use_case.get_recipient(
        ticket=ticket,
        sender_id="client-123",
    )

    assert result == ("agent-456", UserRole.SAV_AGENT)


def test_get_recipient_returns_none_if_client_message_has_no_assigned_agent(
    use_case,
):
    ticket_without_agent = SimpleNamespace(
        user_id="client-123",
        assigned_to=None,
    )

    result = use_case.get_recipient(
        ticket=ticket_without_agent,
        sender_id="client-123",
    )

    assert result is None


def test_get_recipient_returns_client_for_agent_message(
    use_case,
    ticket,
):
    result = use_case.get_recipient(
        ticket=ticket,
        sender_id="agent-456",
    )

    assert result == ("client-123", UserRole.CLIENT)


def test_get_recipient_returns_client_for_other_non_client_sender(
    use_case,
    ticket,
):
    result = use_case.get_recipient(
        ticket=ticket,
        sender_id="another-agent",
    )

    assert result == ("client-123", UserRole.CLIENT)


# =========================================================
# MARK AS READ
# =========================================================

def test_mark_as_read_saves_read_state_commits_and_returns_unread_count(
    use_case,
    ticket_repository,
    read_state_repository,
    unit_of_work,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket
    ticket_repository.count_unread.return_value = 4

    result = use_case.mark_as_read(
        ticket_id="ticket-123",
        user_id="client-123",
        user_role=UserRole.CLIENT,
    )

    assert result == 4

    read_state_repository.mark_last_read.assert_called_once()
    kwargs = read_state_repository.mark_last_read.call_args.kwargs

    assert kwargs["ticket_id"] == "ticket-123"
    assert kwargs["user_id"] == "client-123"
    assert isinstance(kwargs["last_read_at"], datetime)
    assert kwargs["last_read_at"].tzinfo is not None
    assert kwargs["last_read_at"].utcoffset().total_seconds() == 0

    unit_of_work.commit.assert_called_once_with()

    ticket_repository.count_unread.assert_called_once_with(
        user_id="client-123",
        user_role=UserRole.CLIENT,
    )


def test_mark_as_read_checks_access_before_saving(
    use_case,
    ticket_repository,
    read_state_repository,
    unit_of_work,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(TicketAccessDenied):
        use_case.mark_as_read(
            ticket_id="ticket-123",
            user_id="another-client",
            user_role=UserRole.CLIENT,
        )

    read_state_repository.mark_last_read.assert_not_called()
    unit_of_work.commit.assert_not_called()
    ticket_repository.count_unread.assert_not_called()


def test_mark_as_read_raises_if_ticket_does_not_exist(
    use_case,
    ticket_repository,
    read_state_repository,
    unit_of_work,
):
    ticket_repository.get_by_id.return_value = None

    with pytest.raises(SupportTicketNotFound):
        use_case.mark_as_read(
            ticket_id="ticket-123",
            user_id="client-123",
            user_role=UserRole.CLIENT,
        )

    read_state_repository.mark_last_read.assert_not_called()
    unit_of_work.commit.assert_not_called()
    ticket_repository.count_unread.assert_not_called()


def test_mark_as_read_returns_zero_when_no_unread_ticket(
    use_case,
    ticket_repository,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket
    ticket_repository.count_unread.return_value = 0

    result = use_case.mark_as_read(
        ticket_id="ticket-123",
        user_id="client-123",
        user_role=UserRole.CLIENT,
    )

    assert result == 0


def test_mark_as_read_propagates_read_state_error(
    use_case,
    ticket_repository,
    read_state_repository,
    unit_of_work,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket
    read_state_repository.mark_last_read.side_effect = RuntimeError(
        "Erreur de sauvegarde"
    )

    with pytest.raises(RuntimeError, match="Erreur de sauvegarde"):
        use_case.mark_as_read(
            ticket_id="ticket-123",
            user_id="client-123",
            user_role=UserRole.CLIENT,
        )

    unit_of_work.commit.assert_not_called()
    ticket_repository.count_unread.assert_not_called()


def test_mark_as_read_propagates_commit_error(
    use_case,
    ticket_repository,
    unit_of_work,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket
    unit_of_work.commit.side_effect = RuntimeError("Erreur de commit")

    with pytest.raises(RuntimeError, match="Erreur de commit"):
        use_case.mark_as_read(
            ticket_id="ticket-123",
            user_id="client-123",
            user_role=UserRole.CLIENT,
        )

    ticket_repository.count_unread.assert_not_called()


def test_mark_as_read_propagates_unread_count_error(
    use_case,
    ticket_repository,
    unit_of_work,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket
    ticket_repository.count_unread.side_effect = RuntimeError(
        "Erreur de comptage"
    )

    with pytest.raises(RuntimeError, match="Erreur de comptage"):
        use_case.mark_as_read(
            ticket_id="ticket-123",
            user_id="client-123",
            user_role=UserRole.CLIENT,
        )

    unit_of_work.commit.assert_called_once_with()