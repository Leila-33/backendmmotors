from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from modules.auth.domain.enums import UserRole
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
from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.sav.domain.enums import (
    TicketCategory,
    TicketPriority,
    TicketStatus,
)
from modules.sav.domain.exceptions import (
    InvalidTicketState,
    SupportTicketNotFound,
)


# ============================================================
# HELPERS
# ============================================================


def make_ticket(
    *,
    ticket_id: str = "ticket-1",
    user_id: str = "user-1",
    status: TicketStatus = TicketStatus.RESOLVED,
    assigned_to: str | None = "agent-1",
    application_id: str | None = "application-1",
    archived_at=None,
):
    return SupportTicket(
        id=ticket_id,
        user_id=user_id,
        application_id=application_id,
        subject="Problème véhicule",
        description="Description du problème",
        category=TicketCategory.VEHICLE_ISSUE,
        status=status,
        priority=TicketPriority.MEDIUM,
        assigned_to=assigned_to,
        archived_at=archived_at,
    )


def make_dto(
    *,
    ticket_id: str = "ticket-1",
    user_id: str = "agent-1",
    user_role:str = UserRole.SAV_AGENT
):
    return ArchiveSupportTicketDTO(
        ticket_id=ticket_id,
        user_id=user_id,
        user_role=user_role
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def support_ticket_repository():
    return Mock()


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
    return make_dto()


# ============================================================
# TICKET NOT FOUND
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
        use_case.execute(dto=dto)

    support_ticket_repository.get_by_id.assert_called_once_with(
        "ticket-1"
    )

    support_ticket_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# BUSINESS RULE — VALID STATUS
# ============================================================


@pytest.mark.parametrize(
    "status",
    [
        TicketStatus.OPEN,
        TicketStatus.IN_PROGRESS,
        TicketStatus.WAITING_CUSTOMER,
    ],
)
def test_ticket_with_invalid_status_cannot_be_archived(
    status,
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket(
        status=status
    )

    support_ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(InvalidTicketState):
        use_case.execute(dto=dto)

    support_ticket_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


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
        status=status
    )

    updated_ticket = make_ticket(
        status=status
    )

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    result = use_case.execute(
        dto=dto
    )

    assert isinstance(
        result,
        ArchiveSupportTicketResult,
    )

    assert result.ticket is updated_ticket

    support_ticket_repository.update.assert_called_once_with(
        ticket
    )

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# IDEMPOTENCE
# ============================================================


def test_already_archived_ticket_is_returned_without_update(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    archived_at = datetime(
        2026,
        1,
        10,
        12,
        0,
        tzinfo=timezone.utc,
    )

    ticket = make_ticket(
        archived_at=archived_at
    )

    support_ticket_repository.get_by_id.return_value = ticket

    result = use_case.execute(
        dto=dto
    )

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
# ARCHIVE
# ============================================================


def test_ticket_archived_at_is_set(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket()

    updated_ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    use_case.execute(
        dto=dto
    )

    assert ticket.archived_at is not None
    assert isinstance(
        ticket.archived_at,
        datetime,
    )

    assert ticket.archived_at.tzinfo is not None
    assert ticket.archived_at.utcoffset().total_seconds() == 0


def test_archive_uses_utc_datetime(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket()

    updated_ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    use_case.execute(
        dto=dto
    )

    assert ticket.archived_at.tzinfo == timezone.utc


def test_ticket_is_updated_after_archiving(
    use_case,
    support_ticket_repository,
    dto,
):
    ticket = make_ticket()

    updated_ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    use_case.execute(
        dto=dto
    )

    support_ticket_repository.update.assert_called_once_with(
        ticket
    )


# ============================================================
# EVENT
# ============================================================


def test_archive_generates_event(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket(
        status=TicketStatus.RESOLVED,
        assigned_to="agent-1",
        application_id="application-1",
    )

    updated_ticket = make_ticket(
        status=TicketStatus.RESOLVED,
        assigned_to="agent-1",
        application_id="application-1",
    )

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    use_case.execute(
        dto=dto
    )

    event_service.log.assert_called_once_with(
        type=EventType.SUPPORT_TICKET_ARCHIVED,
        message="Ticket SAV archivé",
        application_id="application-1",
        user_id="agent-1",
        event_metadata={
            "ticket_id": "ticket-1",
            "status": "RESOLVED",
            "assigned_to": "agent-1",
            "ticket_owner": "user-1",
        },
    )


def test_archive_event_contains_ticket_information(
    use_case,
    support_ticket_repository,
    event_service,
    dto,
):
    ticket = make_ticket(
        status=TicketStatus.CLOSED
    )

    updated_ticket = make_ticket(
        status=TicketStatus.CLOSED
    )

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    use_case.execute(
        dto=dto
    )

    event_kwargs = (
        event_service.log.call_args.kwargs
    )

    assert (
        event_kwargs["type"]
        == EventType.SUPPORT_TICKET_ARCHIVED
    )

    assert (
        event_kwargs["application_id"]
        == "application-1"
    )

    assert (
        event_kwargs["user_id"]
        == "agent-1"
    )

    assert (
        event_kwargs["event_metadata"]["ticket_id"]
        == "ticket-1"
    )

    assert (
        event_kwargs["event_metadata"]["status"]
        == "CLOSED"
    )

    assert (
        event_kwargs["event_metadata"]["assigned_to"]
        == "agent-1"
    )

    assert (
        event_kwargs["event_metadata"]["ticket_owner"]
        == "user-1"
    )


# ============================================================
# COMMIT
# ============================================================


def test_commit_is_called_after_success(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket()

    updated_ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    use_case.execute(
        dto=dto
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# RESULT
# ============================================================


def test_execute_returns_updated_ticket(
    use_case,
    support_ticket_repository,
    dto,
):
    ticket = make_ticket()

    updated_ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    result = use_case.execute(
        dto=dto
    )

    assert isinstance(
        result,
        ArchiveSupportTicketResult,
    )

    assert result.ticket is updated_ticket


# ============================================================
# ROLLBACK — UPDATE ERROR
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

    support_ticket_repository.update.side_effect = (
        RuntimeError(
            "update error"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        use_case.execute(
            dto=dto
        )

    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — EVENT ERROR
# ============================================================


def test_event_error_rolls_back(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket()

    updated_ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        use_case.execute(
            dto=dto
        )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — COMMIT ERROR
# ============================================================


def test_commit_error_rolls_back(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket()

    updated_ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket
    support_ticket_repository.update.return_value = updated_ticket

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        use_case.execute(
            dto=dto
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# GET TICKET
# ============================================================


def test_ticket_is_loaded_by_id(
    use_case,
    support_ticket_repository,
    dto,
):
    ticket = make_ticket()

    support_ticket_repository.get_by_id.return_value = ticket

    use_case.execute(
        dto=dto
    )

    support_ticket_repository.get_by_id.assert_called_once_with(
        "ticket-1"
    )


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_invalid_state_does_not_update_or_log(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    ticket = make_ticket(
        status=TicketStatus.OPEN
    )

    support_ticket_repository.get_by_id.return_value = ticket

    with pytest.raises(InvalidTicketState):
        use_case.execute(
            dto=dto
        )

    support_ticket_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_not_found_does_not_update_or_log(
    use_case,
    support_ticket_repository,
    event_service,
    unit_of_work,
    dto,
):
    support_ticket_repository.get_by_id.return_value = None

    with pytest.raises(SupportTicketNotFound):
        use_case.execute(
            dto=dto
        )

    support_ticket_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()