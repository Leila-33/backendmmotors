from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from modules.applications.domain.enums import EventType
from modules.sav.application.dtos.agent.archive_support_ticket_dto import (
    ArchiveSupportTicketDTO,
)
from modules.sav.application.results.agent.archive_support_ticket_result import (
    ArchiveSupportTicketResult,
)
from modules.sav.application.use_cases.agent.archive_support_ticket import (
    ArchiveSupportTicketUseCase,
)
from modules.sav.domain.enums import TicketStatus
from modules.sav.domain.exceptions import (
    InvalidTicketState,
    SupportTicketNotFound,
)


# ============================================================
# HELPERS
# ============================================================


def make_ticket(
    *,
    ticket_id="ticket-1",
    application_id="application-1",
    user_id="user-1",
    status=TicketStatus.RESOLVED,
    archived_at=None,
    assigned_to="agent-1",
):
    return SimpleNamespace(
        id=ticket_id,
        application_id=application_id,
        user_id=user_id,
        status=status,
        archived_at=archived_at,
        assigned_to=assigned_to,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def support_ticket_repository():
    repository = Mock()

    repository.update.side_effect = lambda ticket: ticket

    return repository


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    support_ticket_repository,
    event_service,
    unit_of_work,
):
    return ArchiveSupportTicketUseCase(
        support_ticket_repository=support_ticket_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return ArchiveSupportTicketDTO(
        ticket_id="ticket-1",
        user_id="agent-1",
    )


# ============================================================
# NOT FOUND
# ============================================================


def test_ticket_not_found(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    support_ticket_repository.get_by_id.return_value = None

    with pytest.raises(SupportTicketNotFound):
        use_case.execute(dto)

    support_ticket_repository.get_by_id.assert_called_once_with(
        "ticket-1"
    )

    support_ticket_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# INVALID STATE
# ============================================================


@pytest.mark.parametrize(
    "status",
    [
        TicketStatus.OPEN,
        TicketStatus.IN_PROGRESS,
    ],
)
def test_ticket_cannot_be_archived_from_invalid_state(
    status,
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket(
        status=status,
    )

    support_ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(InvalidTicketState):
        use_case.execute(dto)

    support_ticket_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# RESOLVED / CLOSED
# ============================================================


@pytest.mark.parametrize(
    "status",
    [
        TicketStatus.RESOLVED,
        TicketStatus.CLOSED,
    ],
)
def test_resolved_or_closed_ticket_can_be_archived(
    status,
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket(
        status=status,
    )

    support_ticket_repository.get_by_id.return_value = ticket

    result = use_case.execute(dto)

    assert isinstance(
        result,
        ArchiveSupportTicketResult,
    )

    assert result.ticket is ticket

    assert ticket.archived_at is not None
    assert ticket.archived_at.tzinfo == timezone.utc

    support_ticket_repository.update.assert_called_once_with(
        ticket
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# ARCHIVE DATE
# ============================================================


def test_archived_at_is_set_when_ticket_is_archived(
    use_case,
    support_ticket_repository,
    unit_of_work,
    dto,
):
    ticket = make_ticket(
        archived_at=None,
    )

    support_ticket_repository.get_by_id.return_value = ticket

    before = datetime.now(timezone.utc)

    result = use_case.execute(dto)

    after = datetime.now(timezone.utc)

    assert result.ticket.archived_at is not None

    assert before <= result.ticket.archived_at <= after


# ============================================================
# IDEMPOTENCE
# ============================================================


def test_already_archived_ticket_is_not_updated_again(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    archived_at = datetime.now(timezone.utc)

    ticket = make_ticket(
        archived_at=archived_at,
    )

    support_ticket_repository.get_by_id.return_value = ticket

    result = use_case.execute(dto)

    assert isinstance(
        result,
        ArchiveSupportTicketResult,
    )

    assert result.ticket is ticket

    assert result.ticket.archived_at == archived_at

    support_ticket_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# EVENT
# ============================================================


def test_archive_event_is_logged(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket(
        ticket_id="ticket-42",
        application_id="application-42",
        user_id="user-42",
        status=TicketStatus.RESOLVED,
        assigned_to="agent-42",
    )

    support_ticket_repository.get_by_id.return_value = ticket

    use_case.execute(dto)

    event_service.log.assert_called_once_with(
        type=EventType.SUPPORT_TICKET_ARCHIVED,
        message="Ticket SAV archivé",
        application_id="application-42",
        user_id="agent-1",
        event_metadata={
            "ticket_id": "ticket-42",
            "status": TicketStatus.RESOLVED.value,
            "assigned_to": "agent-42",
            "ticket_owner": "user-42",
        },
    )


# ============================================================
# COMMIT
# ============================================================


def test_commit_is_called_after_archiving(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket

    use_case.execute(dto)

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_not_called()


# ============================================================
# RESULT
# ============================================================


def test_updated_ticket_is_returned_in_result(
    use_case,
    support_ticket_repository,
    dto,
):
    ticket = make_ticket()

    updated_ticket = make_ticket(
        archived_at=datetime.now(timezone.utc),
    )

    support_ticket_repository.get_by_id.return_value = ticket

    # Le repository retourne ici explicitement
    # l'objet mis à jour.
    support_ticket_repository.update.side_effect = None
    support_ticket_repository.update.return_value = updated_ticket

    result = use_case.execute(dto)

    assert isinstance(
        result,
        ArchiveSupportTicketResult,
    )

    assert result.ticket is updated_ticket


# ============================================================
# REPOSITORY UPDATE ERROR
# ============================================================


def test_update_error_rolls_back(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket

    support_ticket_repository.update.side_effect = RuntimeError(
        "update error"
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        use_case.execute(dto)

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# EVENT ERROR
# ============================================================


def test_event_error_rolls_back(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(dto)

    support_ticket_repository.update.assert_called_once_with(
        ticket
    )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# COMMIT ERROR
# ============================================================


def test_commit_error_rolls_back(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(dto)

    support_ticket_repository.update.assert_called_once_with(
        ticket
    )

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()