from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Forbidden

from modules.sav.application.dtos.create_ticket_message_dto import (
    CreateTicketMessageDTO,
)
from modules.sav.application.results.create_ticket_message_result import (
    CreateTicketMessageResult,
)
from modules.sav.application.use_cases.create_ticket_message import (
    CreateTicketMessageUseCase,
)

from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.sav.domain.entities.ticket_message import TicketMessage

from modules.sav.domain.enums import (
    TicketCategory,
    TicketPriority,
    TicketStatus,
)

from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    TicketClosedException,
    EmptyMessageException,
    MessageTooLongException,
)


# ============================================================
# HELPERS
# ============================================================


def make_ticket(
    *,
    ticket_id: str = "ticket-123",
    user_id: str = "user-123",
    status: TicketStatus = TicketStatus.OPEN,
):
    return SupportTicket(
        id=ticket_id,
        user_id=user_id,
        application_id="application-123",
        subject="Problème avec mon véhicule",
        description="Description du problème",
        category=TicketCategory.VEHICLE_ISSUE,
        status=status,
        priority=TicketPriority.HIGH,
        assigned_to="agent-123",
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def ticket_repository():
    return Mock()


@pytest.fixture
def message_repository():
    return Mock()


@pytest.fixture
def read_state_repository():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    ticket_repository,
    message_repository,
    read_state_repository,
    unit_of_work,
):
    return CreateTicketMessageUseCase(
        ticket_repository=ticket_repository,
        message_repository=message_repository,
        read_state_repository=read_state_repository,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return CreateTicketMessageDTO(
        ticket_id="ticket-123",
        message="Bonjour, j'ai besoin d'aide.",
    )


@pytest.fixture
def user_id():
    return "user-123"


@pytest.fixture
def user_role():
    return UserRole.CLIENT


@pytest.fixture
def ticket():
    return make_ticket()


@pytest.fixture
def created_message():
    return TicketMessage(
        id="message-123",
        ticket_id="ticket-123",
        sender_id="user-123",
        sender_role=UserRole.CLIENT,
        message="Bonjour, j'ai besoin d'aide.",
        created_at=datetime.now(),
    )


# ============================================================
# TICKET NOT FOUND
# ============================================================


def test_ticket_not_found(
    use_case,
    ticket_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
):
    ticket_repository.get_by_id.return_value = None

    with pytest.raises(SupportTicketNotFound):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    ticket_repository.get_by_id.assert_called_once_with(
        "ticket-123"
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()

    message_repository = use_case.message_repository
    message_repository.create.assert_not_called()


# ============================================================
# AUTHORIZATION
# ============================================================


def test_user_cannot_send_message_on_another_users_ticket(
    use_case,
    ticket_repository,
    message_repository,
    read_state_repository,
    unit_of_work,
    dto,
    user_role,
):
    ticket = make_ticket(
        user_id="owner-123"
    )

    ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(Forbidden):
        use_case.execute(
            dto=dto,
            user_id="another-user",
            user_role=user_role,
        )

    message_repository.create.assert_not_called()
    read_state_repository.mark_last_read.assert_not_called()
    ticket_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_ticket_owner_can_send_message(
    use_case,
    ticket_repository,
    message_repository,
    read_state_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    ticket,
    created_message,
):
    ticket_repository.get_by_id.return_value = ticket
    message_repository.create.return_value = created_message

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert isinstance(
        result,
        CreateTicketMessageResult,
    )

    assert result.message == created_message

    message_repository.create.assert_called_once()

    read_state_repository.mark_last_read.assert_called_once()

    ticket_repository.update.assert_called_once_with(
        ticket
    )

    unit_of_work.commit.assert_called_once()


def test_admin_can_send_message_on_another_users_ticket(
    use_case,
    ticket_repository,
    message_repository,
    read_state_repository,
    unit_of_work,
    dto,
    created_message,
):
    ticket = make_ticket(
        user_id="owner-123"
    )

    ticket_repository.get_by_id.return_value = ticket
    message_repository.create.return_value = created_message

    result = use_case.execute(
        dto=dto,
        user_id="admin-123",
        user_role=UserRole.ADMIN,
    )

    assert isinstance(
        result,
        CreateTicketMessageResult,
    )

    message_repository.create.assert_called_once()

    unit_of_work.commit.assert_called_once()


def test_sav_agent_can_send_message_on_another_users_ticket(
    use_case,
    ticket_repository,
    message_repository,
    unit_of_work,
    dto,
    created_message,
):
    ticket = make_ticket(
        user_id="owner-123"
    )

    ticket_repository.get_by_id.return_value = ticket
    message_repository.create.return_value = created_message

    result = use_case.execute(
        dto=dto,
        user_id="agent-123",
        user_role=UserRole.SAV_AGENT,
    )

    assert isinstance(
        result,
        CreateTicketMessageResult,
    )

    message_repository.create.assert_called_once()

    unit_of_work.commit.assert_called_once()


# ============================================================
# CLOSED TICKET
# ============================================================


def test_closed_ticket_cannot_receive_message(
    use_case,
    ticket_repository,
    message_repository,
    read_state_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
):
    ticket = make_ticket(
        status=TicketStatus.CLOSED
    )

    ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(TicketClosedException):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    message_repository.create.assert_not_called()
    read_state_repository.mark_last_read.assert_not_called()
    ticket_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# MESSAGE VALIDATION
# ============================================================


def test_empty_message_is_rejected(
    use_case,
    ticket_repository,
    message_repository,
    unit_of_work,
    ticket,
    user_id,
    user_role,
):
    ticket_repository.get_by_id.return_value = ticket

    dto = CreateTicketMessageDTO(
        ticket_id="ticket-123",
        message="   ",
    )

    with pytest.raises(EmptyMessageException):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    message_repository.create.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_message_with_only_whitespace_is_rejected(
    use_case,
    ticket_repository,
    message_repository,
    unit_of_work,
    ticket,
    user_id,
    user_role,
):
    ticket_repository.get_by_id.return_value = ticket

    dto = CreateTicketMessageDTO(
        ticket_id="ticket-123",
        message="\n\t   ",
    )

    with pytest.raises(EmptyMessageException):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    message_repository.create.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_message_longer_than_2000_characters_is_rejected(
    use_case,
    ticket_repository,
    message_repository,
    unit_of_work,
    ticket,
    user_id,
    user_role,
):
    ticket_repository.get_by_id.return_value = ticket

    dto = CreateTicketMessageDTO(
        ticket_id="ticket-123",
        message="a" * 2001,
    )

    with pytest.raises(MessageTooLongException):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    message_repository.create.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_message_with_exactly_2000_characters_is_accepted(
    use_case,
    ticket_repository,
    message_repository,
    unit_of_work,
    ticket,
    user_id,
    user_role,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    dto = CreateTicketMessageDTO(
        ticket_id="ticket-123",
        message="a" * 2000,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert result.message == created_message

    message_repository.create.assert_called_once()

    unit_of_work.commit.assert_called_once()


# ============================================================
# MESSAGE CREATION
# ============================================================


def test_message_is_created_with_expected_values(
    use_case,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    with patch(
        "modules.sav.application.use_cases.create_ticket_message.uuid4",
        return_value="message-id",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    message_repository.create.assert_called_once()

    message = (
        message_repository
        .create
        .call_args.args[0]
    )

    assert isinstance(
        message,
        TicketMessage,
    )

    assert message.id == "message-id"
    assert message.ticket_id == "ticket-123"
    assert message.sender_id == "user-123"
    assert message.sender_role == UserRole.CLIENT
    assert message.message == "Bonjour, j'ai besoin d'aide."

    assert isinstance(
        message.created_at,
        datetime,
    )

    assert message.created_at.tzinfo is not None

    assert (
        message.created_at
        .utcoffset()
        .total_seconds()
        == 0
    )


def test_message_content_is_trimmed(
    use_case,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    dto = CreateTicketMessageDTO(
        ticket_id="ticket-123",
        message="   Bonjour le SAV   ",
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    message = (
        message_repository
        .create
        .call_args.args[0]
    )

    assert message.message == "Bonjour le SAV"


# ============================================================
# READ STATE
# ============================================================


def test_last_read_state_is_updated(
    use_case,
    ticket_repository,
    message_repository,
    read_state_repository,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    read_state_repository.mark_last_read.assert_called_once_with(
        ticket_id="ticket-123",
        user_id="user-123",
        last_read_at=created_message.created_at,
    )


# ============================================================
# TICKET UPDATE
# ============================================================


def test_ticket_updated_at_is_updated(
    use_case,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    before = ticket.updated_at

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert ticket.updated_at is not None
    assert ticket.updated_at != before

    assert ticket.updated_at.tzinfo is not None

    assert (
        ticket.updated_at
        .utcoffset()
        .total_seconds()
        == 0
    )


def test_ticket_is_updated_in_repository(
    use_case,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket_repository.update.assert_called_once_with(
        ticket
    )


# ============================================================
# COMMIT / RESULT
# ============================================================


def test_commit_is_called(
    use_case,
    ticket_repository,
    message_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_create_ticket_message_result_is_returned(
    use_case,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert isinstance(
        result,
        CreateTicketMessageResult,
    )

    assert result.message == created_message


# ============================================================
# UUID
# ============================================================


def test_message_uuid_is_generated(
    use_case,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-from-repository"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    with patch(
        "modules.sav.application.use_cases.create_ticket_message.uuid4",
        return_value="generated-message-id",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    message = (
        message_repository
        .create
        .call_args.args[0]
    )

    assert message.id == "generated-message-id"


# ============================================================
# ROLLBACK — MESSAGE REPOSITORY
# ============================================================


def test_message_creation_error_rolls_back(
    use_case,
    ticket_repository,
    message_repository,
    read_state_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    message_repository.create.side_effect = RuntimeError(
        "message repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="message repository error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()

    read_state_repository.mark_last_read.assert_not_called()
    ticket_repository.update.assert_not_called()


# ============================================================
# ROLLBACK — READ STATE
# ============================================================


def test_read_state_error_rolls_back(
    use_case,
    ticket_repository,
    message_repository,
    read_state_repository,
    ticket,
    unit_of_work,
    dto,
    user_id,
    user_role,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    read_state_repository.mark_last_read.side_effect = RuntimeError(
        "read state error"
    )

    with pytest.raises(
        RuntimeError,
        match="read state error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()

    ticket_repository.update.assert_not_called()


# ============================================================
# ROLLBACK — TICKET UPDATE
# ============================================================


def test_ticket_update_error_rolls_back(
    use_case,
    ticket_repository,
    message_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    ticket_repository.update.side_effect = RuntimeError(
        "ticket update error"
    )

    with pytest.raises(
        RuntimeError,
        match="ticket update error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# ROLLBACK — COMMIT
# ============================================================


def test_commit_error_rolls_back(
    use_case,
    ticket_repository,
    message_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    ticket,
):
    ticket_repository.get_by_id.return_value = ticket

    created_message = Mock()
    created_message.id = "message-123"
    created_message.created_at = datetime.now()

    message_repository.create.return_value = created_message

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — TICKET LOADING
# ============================================================


def test_ticket_loading_error_rolls_back(
    use_case,
    ticket_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
):
    ticket_repository.get_by_id.side_effect = RuntimeError(
        "ticket repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="ticket repository error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# NO UNEXPECTED OPERATIONS AFTER VALIDATION ERRORS
# ============================================================


@pytest.mark.parametrize(
    "status,exception",
    [
        (
            TicketStatus.CLOSED,
            TicketClosedException,
        ),
    ],
)
def test_no_message_created_when_ticket_cannot_receive_messages(
    use_case,
    ticket_repository,
    message_repository,
    read_state_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    status,
    exception,
):
    ticket_repository.get_by_id.return_value = make_ticket(
        status=status
    )

    with pytest.raises(exception):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    message_repository.create.assert_not_called()
    read_state_repository.mark_last_read.assert_not_called()
    ticket_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()