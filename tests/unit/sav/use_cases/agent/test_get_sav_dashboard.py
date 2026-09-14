from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from modules.sav.application.results.agent.get_sav_dashboard_result import (
    GetSavDashboardResult,
    SavDashboardTicketResult,
)
from modules.sav.application.use_cases.agent.get_sav_dashboard import (
    GetSavDashboardUseCase,
)
from modules.sav.domain.enums import (
    TicketPriority,
    TicketStatus,
)


# ============================================================
# HELPERS
# ============================================================


def make_ticket(
    *,
    ticket_id: str = "ticket-1",
    subject: str = "Problème véhicule",
    priority: TicketPriority = TicketPriority.MEDIUM,
    status: TicketStatus = TicketStatus.OPEN,
    created_at: datetime | None = None,
):
    return Mock(
        id=ticket_id,
        subject=subject,
        priority=priority,
        status=status,
        created_at=created_at
        or datetime(
            2026,
            1,
            15,
            10,
            30,
            tzinfo=timezone.utc,
        ),
    )


def make_dashboard_data(
    *,
    total: int = 10,
    open: int = 4,
    urgent: int = 2,
    recent_tickets=None,
):
    return {
        "total": total,
        "open": open,
        "urgent": urgent,
        "recent_tickets": (
            []
            if recent_tickets is None
            else recent_tickets
        ),
    }


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repo():
    return Mock()


@pytest.fixture
def use_case(repo):
    return GetSavDashboardUseCase(
        repo=repo
    )


@pytest.fixture
def user_id():
    return "agent-123"


# ============================================================
# BASIC
# ============================================================


def test_execute_calls_repository_with_user_id(
    use_case,
    repo,
    user_id,
):
    repo.get_dashboard_stats.return_value = (
        make_dashboard_data()
    )

    use_case.execute(
        user_id=user_id
    )

    repo.get_dashboard_stats.assert_called_once_with(
        user_id=user_id
    )


def test_execute_returns_dashboard_result(
    use_case,
    repo,
    user_id,
):
    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            total=10,
            open=4,
            urgent=2,
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert isinstance(
        result,
        GetSavDashboardResult,
    )


# ============================================================
# COUNTERS
# ============================================================


def test_execute_returns_total_count(
    use_case,
    repo,
    user_id,
):
    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            total=25,
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.total == 25


def test_execute_returns_open_count(
    use_case,
    repo,
    user_id,
):
    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            open=8,
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.open == 8


def test_execute_returns_urgent_count(
    use_case,
    repo,
    user_id,
):
    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            urgent=3,
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.urgent == 3


@pytest.mark.parametrize(
    "total,open_count,urgent",
    [
        (0, 0, 0),
        (1, 1, 0),
        (10, 4, 2),
        (100, 25, 8),
    ],
)
def test_execute_preserves_dashboard_counts(
    total,
    open_count,
    urgent,
    use_case,
    repo,
    user_id,
):
    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            total=total,
            open=open_count,
            urgent=urgent,
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.total == total
    assert result.open == open_count
    assert result.urgent == urgent


# ============================================================
# RECENT TICKETS
# ============================================================


def test_execute_returns_empty_recent_tickets(
    use_case,
    repo,
    user_id,
):
    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            recent_tickets=[]
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert result.recent_tickets == []


def test_execute_transforms_recent_ticket(
    use_case,
    repo,
    user_id,
):
    created_at = datetime(
        2026,
        2,
        10,
        14,
        30,
        tzinfo=timezone.utc,
    )

    ticket = make_ticket(
        ticket_id="ticket-42",
        subject="Problème de livraison",
        priority=TicketPriority.HIGH,
        status=TicketStatus.IN_PROGRESS,
        created_at=created_at,
    )

    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            recent_tickets=[ticket]
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert len(result.recent_tickets) == 1

    dashboard_ticket = (
        result.recent_tickets[0]
    )

    assert isinstance(
        dashboard_ticket,
        SavDashboardTicketResult,
    )

    assert dashboard_ticket.id == "ticket-42"
    assert (
        dashboard_ticket.subject
        == "Problème de livraison"
    )
    assert (
        dashboard_ticket.priority
        == TicketPriority.HIGH
    )
    assert (
        dashboard_ticket.status
        == TicketStatus.IN_PROGRESS
    )
    assert (
        dashboard_ticket.created_at
        == created_at
    )


def test_execute_transforms_multiple_recent_tickets(
    use_case,
    repo,
    user_id,
):
    ticket_1 = make_ticket(
        ticket_id="ticket-1",
        subject="Premier ticket",
        priority=TicketPriority.LOW,
        status=TicketStatus.OPEN,
    )

    ticket_2 = make_ticket(
        ticket_id="ticket-2",
        subject="Deuxième ticket",
        priority=TicketPriority.URGENT,
        status=TicketStatus.RESOLVED,
    )

    ticket_3 = make_ticket(
        ticket_id="ticket-3",
        subject="Troisième ticket",
        priority=TicketPriority.MEDIUM,
        status=TicketStatus.CLOSED,
    )

    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            recent_tickets=[
                ticket_1,
                ticket_2,
                ticket_3,
            ]
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert len(result.recent_tickets) == 3

    assert result.recent_tickets[0].id == "ticket-1"
    assert (
        result.recent_tickets[0].subject
        == "Premier ticket"
    )

    assert result.recent_tickets[1].id == "ticket-2"
    assert (
        result.recent_tickets[1].priority
        == TicketPriority.URGENT
    )

    assert result.recent_tickets[2].id == "ticket-3"
    assert (
        result.recent_tickets[2].status
        == TicketStatus.CLOSED
    )


def test_execute_preserves_recent_ticket_order(
    use_case,
    repo,
    user_id,
):
    tickets = [
        make_ticket(ticket_id="ticket-1"),
        make_ticket(ticket_id="ticket-2"),
        make_ticket(ticket_id="ticket-3"),
    ]

    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            recent_tickets=tickets
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert [
        ticket.id
        for ticket in result.recent_tickets
    ] == [
        "ticket-1",
        "ticket-2",
        "ticket-3",
    ]


# ============================================================
# COMPLETE RESULT
# ============================================================


def test_execute_returns_complete_dashboard(
    use_case,
    repo,
    user_id,
):
    created_at = datetime(
        2026,
        3,
        1,
        9,
        15,
        tzinfo=timezone.utc,
    )

    ticket = make_ticket(
        ticket_id="ticket-99",
        subject="Demande client",
        priority=TicketPriority.URGENT,
        status=TicketStatus.OPEN,
        created_at=created_at,
    )

    repo.get_dashboard_stats.return_value = (
        make_dashboard_data(
            total=20,
            open=7,
            urgent=3,
            recent_tickets=[ticket],
        )
    )

    result = use_case.execute(
        user_id=user_id
    )

    assert isinstance(
        result,
        GetSavDashboardResult,
    )

    assert result.total == 20
    assert result.open == 7
    assert result.urgent == 3

    assert len(result.recent_tickets) == 1

    dashboard_ticket = (
        result.recent_tickets[0]
    )

    assert dashboard_ticket.id == "ticket-99"
    assert dashboard_ticket.subject == "Demande client"
    assert (
        dashboard_ticket.priority
        == TicketPriority.URGENT
    )
    assert (
        dashboard_ticket.status
        == TicketStatus.OPEN
    )
    assert (
        dashboard_ticket.created_at
        == created_at
    )


# ============================================================
# ERROR
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    repo,
    user_id,
):
    repo.get_dashboard_stats.side_effect = RuntimeError(
        "dashboard repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="dashboard repository error",
    ):
        use_case.execute(
            user_id=user_id
        )

    repo.get_dashboard_stats.assert_called_once_with(
        user_id=user_id
    )


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_execute_only_reads_dashboard_data(
    use_case,
    repo,
    user_id,
):
    repo.get_dashboard_stats.return_value = (
        make_dashboard_data()
    )

    use_case.execute(
        user_id=user_id
    )

    repo.get_dashboard_stats.assert_called_once_with(
        user_id=user_id
    )

    repo.create.assert_not_called()
    repo.update.assert_not_called()
    repo.delete.assert_not_called()