from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from modules.applications.domain.enums import EventType
from modules.auth.domain.enums import UserRole

from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.sav.domain.enums import (
    TicketCategory,
    TicketPriority,
    TicketStatus,
)

from modules.sav.application.dtos.create_support_ticket_dto import (
    CreateSupportTicketDTO,
)
from modules.sav.application.results.create_support_ticket_result import (
    CreateSupportTicketResult,
)
from modules.sav.application.use_cases.create_support_ticket import (
    CreateSupportTicketUseCase,
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
def assignment_service():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    ticket_repository,
    message_repository,
    assignment_service,
    event_service,
    unit_of_work,
):
    return CreateSupportTicketUseCase(
        ticket_repository=ticket_repository,
        message_repository=message_repository,
        assignment_service=assignment_service,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return CreateSupportTicketDTO(
        subject="Problème avec mon véhicule",
        category=TicketCategory.VEHICLE_ISSUE,
        message="J'ai un problème avec mon véhicule.",
        priority=TicketPriority.HIGH,
        application_id="application-123",
    )


@pytest.fixture
def user_id():
    return "user-123"


@pytest.fixture
def user_role():
    return UserRole.CLIENT


@pytest.fixture
def agent():
    agent = Mock()
    agent.id = "agent-123"
    return agent


@pytest.fixture
def created_ticket():
    return SupportTicket(
        id="ticket-123",
        user_id="user-123",
        application_id="application-123",
        subject="Problème avec mon véhicule",
        description="J'ai un problème avec mon véhicule.",
        category=TicketCategory.VEHICLE_ISSUE,
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        assigned_to="agent-123",
    )


# ============================================================
# ASSIGNMENT
# ============================================================


def test_execute_gets_next_agent(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assignment_service.get_next_agent.assert_called_once()


def test_execute_assigns_agent_to_ticket(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.assigned_to == "agent-123"


def test_execute_creates_ticket_without_agent(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
):
    assignment_service.get_next_agent.return_value = None

    created_ticket = SupportTicket(
        id="ticket-123",
        user_id="user-123",
        application_id="application-123",
        subject="Problème avec mon véhicule",
        description="J'ai un problème avec mon véhicule.",
        category=TicketCategory.VEHICLE_ISSUE,
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        assigned_to=None,
    )

    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.assigned_to is None


# ============================================================
# TICKET CREATION
# ============================================================


def test_execute_creates_ticket(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket_repository.create.assert_called_once()


def test_execute_creates_support_ticket_entity(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert isinstance(ticket, SupportTicket)


def test_execute_creates_ticket_with_correct_data(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.user_id == user_id
    assert ticket.application_id == "application-123"

    assert ticket.subject == "Problème avec mon véhicule"

    assert ticket.description == (
        "J'ai un problème avec mon véhicule."
    )

    assert ticket.category == TicketCategory.VEHICLE_ISSUE
    assert ticket.status == TicketStatus.OPEN
    assert ticket.priority == TicketPriority.HIGH

    assert ticket.assigned_to == "agent-123"


def test_execute_ticket_status_is_open(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.status == TicketStatus.OPEN


# ============================================================
# APPLICATION ID
# ============================================================


def test_execute_strips_application_id(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    dto.application_id = "  application-123  "

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.application_id == "application-123"


def test_execute_accepts_none_application_id(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    dto.application_id = None

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.application_id is None


# ============================================================
# SUBJECT / MESSAGE
# ============================================================


def test_execute_strips_subject(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    dto.subject = "  Mon problème  "

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.subject == "Mon problème"


def test_execute_strips_message_for_ticket_description(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    dto.message = "  Description du problème  "

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.description == "Description du problème"


# ============================================================
# FIRST MESSAGE
# ============================================================


def test_execute_creates_first_message(
    use_case,
    assignment_service,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    message_repository.create.assert_called_once()

    message = message_repository.create.call_args.args[0]

    assert message.ticket_id == "ticket-123"
    assert message.sender_id == user_id
    assert message.sender_role == user_role
    assert message.message == dto.message.strip()


def test_execute_strips_first_message(
    use_case,
    assignment_service,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    dto.message = "  Bonjour, j'ai un problème.  "

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    message = message_repository.create.call_args.args[0]

    assert message.message == (
        "Bonjour, j'ai un problème."
    )


def test_execute_first_message_belongs_to_created_ticket(
    use_case,
    assignment_service,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    message = message_repository.create.call_args.args[0]

    assert message.ticket_id == created_ticket.id


# ============================================================
# EVENT
# ============================================================


def test_execute_logs_support_ticket_created_event(
    use_case,
    assignment_service,
    ticket_repository,
    event_service,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    event_service.log.assert_called_once_with(
        type=EventType.SUPPORT_TICKET_CREATED,
        message="Ticket SAV créé",
        application_id="application-123",
        user_id="user-123",
        event_metadata={
            "ticket_id": "ticket-123",
            "subject": "Problème avec mon véhicule",
            "category": TicketCategory.VEHICLE_ISSUE.value,
            "priority": TicketPriority.HIGH.value,
            "assigned_to": "agent-123",
        },
    )


# ============================================================
# COMMIT
# ============================================================


def test_execute_commits_transaction(
    use_case,
    assignment_service,
    ticket_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# RESULT
# ============================================================


def test_execute_returns_create_support_ticket_result(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert isinstance(
        result,
        CreateSupportTicketResult,
    )

    assert result.ticket is created_ticket


# ============================================================
# UUID
# ============================================================


def test_execute_generates_ticket_id(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    with patch(
        "modules.sav.application.use_cases.create_support_ticket.uuid4",
        return_value="generated-ticket-id",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    ticket = ticket_repository.create.call_args.args[0]

    assert ticket.id == "generated-ticket-id"


def test_execute_generates_message_id(
    use_case,
    assignment_service,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    with patch(
        "modules.sav.application.use_cases.create_support_ticket.uuid4",
        side_effect=[
            "generated-ticket-id",
            "generated-message-id",
        ],
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    message = message_repository.create.call_args.args[0]

    assert message.id == "generated-message-id"


# ============================================================
# UTC DATES
# ============================================================


def test_execute_creates_timezone_aware_ticket_date(
    use_case,
    assignment_service,
    ticket_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    ticket = ticket_repository.create.call_args.args[0]

    assert isinstance(
        ticket.created_at,
        datetime,
    )

    assert ticket.created_at.tzinfo is not None

    assert (
        ticket.created_at
        .utcoffset()
        .total_seconds()
        == 0
    )


def test_execute_creates_timezone_aware_message_date(
    use_case,
    assignment_service,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    message = message_repository.create.call_args.args[0]

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


# ============================================================
# ROLLBACK / ERRORS
# ============================================================


def test_execute_rolls_back_when_ticket_creation_fails(
    use_case,
    assignment_service,
    ticket_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
):
    assignment_service.get_next_agent.return_value = None

    ticket_repository.create.side_effect = RuntimeError(
        "Ticket creation error"
    )

    with pytest.raises(
        RuntimeError,
        match="Ticket creation error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_execute_rolls_back_when_message_creation_fails(
    use_case,
    assignment_service,
    ticket_repository,
    message_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    message_repository.create.side_effect = RuntimeError(
        "Message creation error"
    )

    with pytest.raises(
        RuntimeError,
        match="Message creation error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_execute_rolls_back_when_event_logging_fails(
    use_case,
    assignment_service,
    ticket_repository,
    event_service,
    unit_of_work,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    event_service.log.side_effect = RuntimeError(
        "Event logging error"
    )

    with pytest.raises(
        RuntimeError,
        match="Event logging error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    assignment_service,
    ticket_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_assignment_fails(
    use_case,
    assignment_service,
    unit_of_work,
    dto,
    user_id,
    user_role,
):
    assignment_service.get_next_agent.side_effect = RuntimeError(
        "Assignment error"
    )

    with pytest.raises(
        RuntimeError,
        match="Assignment error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# NO UNEXPECTED OPERATIONS AFTER FAILURE
# ============================================================


def test_ticket_creation_error_does_not_create_message(
    use_case,
    assignment_service,
    ticket_repository,
    message_repository,
    dto,
    user_id,
    user_role,
):
    assignment_service.get_next_agent.return_value = None

    ticket_repository.create.side_effect = RuntimeError(
        "Ticket creation error"
    )

    with pytest.raises(RuntimeError):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    message_repository.create.assert_not_called()


def test_message_creation_error_does_not_log_event(
    use_case,
    assignment_service,
    ticket_repository,
    message_repository,
    event_service,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    message_repository.create.side_effect = RuntimeError(
        "Message creation error"
    )

    with pytest.raises(RuntimeError):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    event_service.log.assert_not_called()


def test_event_error_does_not_commit(
    use_case,
    assignment_service,
    ticket_repository,
    event_service,
    unit_of_work,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    event_service.log.side_effect = RuntimeError(
        "Event logging error"
    )

    with pytest.raises(RuntimeError):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.commit.assert_not_called()


def test_commit_error_rolls_back(
    use_case,
    assignment_service,
    ticket_repository,
    unit_of_work,
    dto,
    user_id,
    user_role,
    agent,
    created_ticket,
):
    assignment_service.get_next_agent.return_value = agent
    ticket_repository.create.return_value = created_ticket

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(RuntimeError):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

    unit_of_work.rollback.assert_called_once()