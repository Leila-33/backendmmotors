from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.auth.domain.enums import UserRole
from modules.sav.application.results.create_support_ticket_result import (
    CreateSupportTicketResult,
)
from modules.sav.application.use_cases.create_support_ticket import (
    CreateSupportTicketUseCase,
)
from modules.sav.domain.enums import TicketStatus


# ============================================================
# HELPERS
# ============================================================


class FakeEnum:
    """
    Petit faux enum permettant de reproduire uniquement
    l'attribut `.value` utilisé par le use case.
    """

    def __init__(self, value):
        self.value = value


def make_dto(
    *,
    application_id="application-1",
    subject="Problème avec mon véhicule",
    message="Je rencontre un problème avec mon véhicule.",
    category_value="technical",
    priority_value="normal",
):
    return SimpleNamespace(
        application_id=application_id,
        subject=subject,
        message=message,
        category=FakeEnum(category_value),
        priority=FakeEnum(priority_value),
    )


def make_application(
    *,
    application_id="application-1",
):
    return SimpleNamespace(
        id=application_id,
    )


def make_agent(
    *,
    agent_id="agent-1",
):
    return SimpleNamespace(
        id=agent_id,
    )


def make_ticket(
    *,
    ticket_id="ticket-1",
    user_id="user-1",
    application_id=None,
    subject="Problème avec mon véhicule",
    description="Je rencontre un problème avec mon véhicule.",
    category_value="technical",
    priority_value="normal",
    assigned_to="agent-1",
):
    return SimpleNamespace(
        id=ticket_id,
        user_id=user_id,
        application_id=application_id,
        subject=subject,
        description=description,
        category=FakeEnum(category_value),
        priority=FakeEnum(priority_value),
        status=TicketStatus.OPEN,
        assigned_to=assigned_to,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def ticket_repository():
    """
    Le repository retourne un ticket par défaut.

    Important :
    on n'utilise PAS de side_effect ici, car side_effect
    est prioritaire sur return_value.
    """
    repository = Mock()

    repository.create.return_value = make_ticket(
        ticket_id="ticket-1",
        application_id=None,
    )

    return repository


@pytest.fixture
def message_repository():
    return Mock()


@pytest.fixture
def assignment_service():
    service = Mock()

    service.get_next_agent.return_value = make_agent()

    return service


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def application_repository():
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
    application_repository,
    unit_of_work,
):
    return CreateSupportTicketUseCase(
        ticket_repository=ticket_repository,
        message_repository=message_repository,
        assignment_service=assignment_service,
        event_service=event_service,
        application_repository=application_repository,
        unit_of_work=unit_of_work,
    )


# ============================================================
# APPLICATION
# ============================================================


def test_application_is_loaded_when_application_id_is_provided(
    use_case,
    application_repository,
    ticket_repository,
):
    application = make_application(
        application_id="application-42",
    )

    application_repository.get_by_id.return_value = application

    ticket_repository.create.return_value = make_ticket(
        ticket_id="ticket-42",
        application_id="application-42",
    )

    dto = make_dto(
        application_id="application-42",
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    application_repository.get_by_id.assert_called_once_with(
        "application-42"
    )


def test_application_not_found(
    use_case,
    application_repository,
    unit_of_work,
):
    application_repository.get_by_id.return_value = None

    dto = make_dto(
        application_id="application-42",
    )

    with pytest.raises(ApplicationNotFound):
        use_case.execute(
            dto=dto,
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_no_application_lookup_when_application_id_is_missing(
    use_case,
    application_repository,
):
    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    application_repository.get_by_id.assert_not_called()


def test_application_id_is_stripped(
    use_case,
    application_repository,
    ticket_repository,
):
    application = make_application(
        application_id="application-42",
    )

    application_repository.get_by_id.return_value = application

    ticket_repository.create.return_value = make_ticket(
        ticket_id="ticket-42",
        application_id="application-42",
    )

    dto = make_dto(
        application_id="  application-42  ",
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    application_repository.get_by_id.assert_called_once_with(
        "application-42"
    )


# ============================================================
# ASSIGNMENT
# ============================================================


def test_ticket_is_assigned_to_next_agent(
    use_case,
    assignment_service,
    ticket_repository,
):
    agent = make_agent(
        agent_id="agent-42",
    )

    assignment_service.get_next_agent.return_value = agent

    ticket_repository.create.return_value = make_ticket(
        ticket_id="ticket-42",
        assigned_to="agent-42",
    )

    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.assigned_to == "agent-42"


def test_ticket_has_no_agent_when_no_agent_is_available(
    use_case,
    assignment_service,
    ticket_repository,
):
    assignment_service.get_next_agent.return_value = None

    ticket_repository.create.return_value = make_ticket(
        ticket_id="ticket-42",
        assigned_to=None,
    )

    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.assigned_to is None


# ============================================================
# TICKET CREATION
# ============================================================


def test_ticket_is_created(
    use_case,
    ticket_repository,
):
    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    ticket_repository.create.assert_called_once()


def test_ticket_contains_user_id(
    use_case,
    ticket_repository,
):
    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-42",
        user_role=UserRole.CLIENT,
    )

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.user_id == "user-42"


def test_ticket_contains_application_id(
    use_case,
    application_repository,
    ticket_repository,
):
    application = make_application(
        application_id="application-42",
    )

    application_repository.get_by_id.return_value = application

    ticket_repository.create.return_value = make_ticket(
        ticket_id="ticket-42",
        application_id="application-42",
    )

    dto = make_dto(
        application_id="application-42",
    )

    use_case.execute(
        dto=dto,
        user_id="user-42",
        user_role=UserRole.CLIENT,
    )

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.application_id == "application-42"


def test_ticket_contains_stripped_subject(
    use_case,
    ticket_repository,
):
    dto = make_dto(
        application_id=None,
        subject="  Problème véhicule  ",
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.subject == "Problème véhicule"


def test_ticket_contains_stripped_message_as_description(
    use_case,
    ticket_repository,
):
    dto = make_dto(
        application_id=None,
        message="  Je rencontre un problème.  ",
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.description == (
        "Je rencontre un problème."
    )


def test_ticket_has_open_status(
    use_case,
    ticket_repository,
):
    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.status == TicketStatus.OPEN


def test_ticket_contains_category(
    use_case,
    ticket_repository,
):
    dto = make_dto(
        application_id=None,
        category_value="technical",
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.category.value == "technical"


def test_ticket_contains_priority(
    use_case,
    ticket_repository,
):
    dto = make_dto(
        application_id=None,
        priority_value="normal",
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.priority.value == "normal"


# ============================================================
# FIRST MESSAGE
# ============================================================


def test_first_message_is_created(
    use_case,
    message_repository,
):
    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    message_repository.create.assert_called_once()


def test_first_message_is_linked_to_created_ticket(
    use_case,
    ticket_repository,
    message_repository,
):
    ticket = make_ticket(
        ticket_id="ticket-42",
        application_id=None,
    )

    ticket_repository.create.return_value = ticket

    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    message = message_repository.create.call_args.args[0]

    assert message.ticket_id == "ticket-42"


def test_first_message_contains_user_id(
    use_case,
    message_repository,
):
    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-42",
        user_role=UserRole.CLIENT,
    )

    message = message_repository.create.call_args.args[0]

    assert message.sender_id == "user-42"


def test_first_message_contains_user_role(
    use_case,
    message_repository,
):
    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-42",
        user_role=UserRole.CLIENT,
    )

    message = message_repository.create.call_args.args[0]

    assert message.sender_role == UserRole.CLIENT


def test_first_message_contains_stripped_message(
    use_case,
    message_repository,
):
    dto = make_dto(
        application_id=None,
        message="  Mon problème est urgent.  ",
    )

    use_case.execute(
        dto=dto,
        user_id="user-42",
        user_role=UserRole.CLIENT,
    )

    message = message_repository.create.call_args.args[0]

    assert message.message == "Mon problème est urgent."


# ============================================================
# EVENT
# ============================================================


def test_support_ticket_created_event_is_logged(
    use_case,
    ticket_repository,
    application_repository,
    event_service,
):
    application = make_application(
        application_id="application-42",
    )

    ticket = make_ticket(
        ticket_id="ticket-42",
        user_id="user-42",
        application_id="application-42",
        subject="Problème véhicule",
        category_value="technical",
        priority_value="normal",
        assigned_to="agent-42",
    )

    application_repository.get_by_id.return_value = application
    ticket_repository.create.return_value = ticket

    dto = make_dto(
        application_id="application-42",
        subject="Problème véhicule",
        category_value="technical",
        priority_value="normal",
    )

    use_case.execute(
        dto=dto,
        user_id="user-42",
        user_role=UserRole.CLIENT,
    )

    event_service.log.assert_called_once()

    kwargs = event_service.log.call_args.kwargs

    assert kwargs["type"] == EventType.SUPPORT_TICKET_CREATED
    assert kwargs["message"] == "Ticket SAV créé"
    assert kwargs["application_id"] == "application-42"
    assert kwargs["user_id"] == "user-42"

    assert kwargs["event_metadata"] == {
        "ticket_id": "ticket-42",
        "subject": "Problème véhicule",
        "category": "technical",
        "priority": "normal",
        "assigned_to": "agent-42",
    }


def test_event_contains_ticket_id(
    use_case,
    ticket_repository,
    event_service,
):
    ticket = make_ticket(
        ticket_id="ticket-42",
        application_id=None,
    )

    ticket_repository.create.return_value = ticket

    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    kwargs = event_service.log.call_args.kwargs

    assert kwargs["event_metadata"]["ticket_id"] == "ticket-42"


def test_event_contains_assigned_agent(
    use_case,
    ticket_repository,
    assignment_service,
    event_service,
):
    ticket = make_ticket(
        ticket_id="ticket-42",
        application_id=None,
        assigned_to="agent-42",
    )

    ticket_repository.create.return_value = ticket

    assignment_service.get_next_agent.return_value = make_agent(
        agent_id="agent-42",
    )

    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    kwargs = event_service.log.call_args.kwargs

    assert (
        kwargs["event_metadata"]["assigned_to"]
        == "agent-42"
    )


# ============================================================
# RESULT
# ============================================================


def test_create_support_ticket_result_is_returned(
    use_case,
    ticket_repository,
):
    ticket = make_ticket(
        ticket_id="ticket-42",
        application_id=None,
    )

    ticket_repository.create.return_value = ticket

    dto = make_dto(
        application_id=None,
    )

    result = use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert isinstance(
        result,
        CreateSupportTicketResult,
    )

    assert result.ticket is ticket


def test_result_contains_created_ticket(
    use_case,
    ticket_repository,
):
    ticket = make_ticket(
        ticket_id="ticket-42",
        application_id=None,
    )

    ticket_repository.create.return_value = ticket

    dto = make_dto(
        application_id=None,
    )

    result = use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert result.ticket.id == "ticket-42"


# ============================================================
# UNIT OF WORK
# ============================================================


def test_commit_is_called(
    use_case,
    unit_of_work,
):
    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    unit_of_work.commit.assert_called_once()


def test_rollback_is_not_called_on_success(
    use_case,
    unit_of_work,
):
    dto = make_dto(
        application_id=None,
    )

    use_case.execute(
        dto=dto,
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    unit_of_work.rollback.assert_not_called()


# ============================================================
# ERRORS / ROLLBACK
# ============================================================


def test_ticket_creation_error_rolls_back(
    use_case,
    ticket_repository,
    unit_of_work,
):
    ticket_repository.create.side_effect = RuntimeError(
        "ticket creation error"
    )

    dto = make_dto(
        application_id=None,
    )

    with pytest.raises(
        RuntimeError,
        match="ticket creation error",
    ):
        use_case.execute(
            dto=dto,
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_message_creation_error_rolls_back(
    use_case,
    message_repository,
    unit_of_work,
):
    message_repository.create.side_effect = RuntimeError(
        "message creation error"
    )

    dto = make_dto(
        application_id=None,
    )

    with pytest.raises(
        RuntimeError,
        match="message creation error",
    ):
        use_case.execute(
            dto=dto,
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_event_logging_error_rolls_back(
    use_case,
    event_service,
    unit_of_work,
):
    event_service.log.side_effect = RuntimeError(
        "event logging error"
    )

    dto = make_dto(
        application_id=None,
    )

    with pytest.raises(
        RuntimeError,
        match="event logging error",
    ):
        use_case.execute(
            dto=dto,
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_commit_error_rolls_back(
    use_case,
    unit_of_work,
):
    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    dto = make_dto(
        application_id=None,
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(
            dto=dto,
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


def test_application_lookup_error_rolls_back(
    use_case,
    application_repository,
    unit_of_work,
):
    application_repository.get_by_id.side_effect = RuntimeError(
        "application repository error"
    )

    dto = make_dto(
        application_id="application-42",
    )

    with pytest.raises(
        RuntimeError,
        match="application repository error",
    ):
        use_case.execute(
            dto=dto,
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_assignment_error_rolls_back(
    use_case,
    assignment_service,
    unit_of_work,
):
    assignment_service.get_next_agent.side_effect = RuntimeError(
        "assignment error"
    )

    dto = make_dto(
        application_id=None,
    )

    with pytest.raises(
        RuntimeError,
        match="assignment error",
    ):
        use_case.execute(
            dto=dto,
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# COMPLETE FLOW
# ============================================================


def test_create_support_ticket_complete_flow(
    use_case,
    ticket_repository,
    message_repository,
    event_service,
    application_repository,
    assignment_service,
    unit_of_work,
):
    application = make_application(
        application_id="application-42",
    )

    ticket = make_ticket(
        ticket_id="ticket-42",
        user_id="user-42",
        application_id="application-42",
        subject="Problème véhicule",
        description="Je rencontre un problème.",
        category_value="technical",
        priority_value="normal",
        assigned_to="agent-42",
    )

    application_repository.get_by_id.return_value = application

    assignment_service.get_next_agent.return_value = make_agent(
        agent_id="agent-42",
    )

    ticket_repository.create.return_value = ticket

    dto = make_dto(
        application_id="application-42",
        subject="Problème véhicule",
        message="Je rencontre un problème.",
        category_value="technical",
        priority_value="normal",
    )

    result = use_case.execute(
        dto=dto,
        user_id="user-42",
        user_role=UserRole.CLIENT,
    )

    # Résultat
    assert isinstance(
        result,
        CreateSupportTicketResult,
    )

    assert result.ticket is ticket

    # Ticket
    ticket_repository.create.assert_called_once()

    created_ticket = ticket_repository.create.call_args.args[0]

    assert created_ticket.user_id == "user-42"
    assert created_ticket.application_id == "application-42"
    assert created_ticket.subject == "Problème véhicule"
    assert created_ticket.description == (
        "Je rencontre un problème."
    )
    assert created_ticket.status == TicketStatus.OPEN
    assert created_ticket.assigned_to == "agent-42"

    # Premier message
    message_repository.create.assert_called_once()

    message = message_repository.create.call_args.args[0]

    assert message.ticket_id == "ticket-42"
    assert message.sender_id == "user-42"
    assert message.sender_role == UserRole.CLIENT
    assert message.message == "Je rencontre un problème."

    # Événement
    event_service.log.assert_called_once()

    event_kwargs = event_service.log.call_args.kwargs

    assert event_kwargs["type"] == EventType.SUPPORT_TICKET_CREATED
    assert event_kwargs["application_id"] == "application-42"
    assert event_kwargs["user_id"] == "user-42"

    assert event_kwargs["event_metadata"] == {
        "ticket_id": "ticket-42",
        "subject": "Problème véhicule",
        "category": "technical",
        "priority": "normal",
        "assigned_to": "agent-42",
    }

    # Transaction
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()