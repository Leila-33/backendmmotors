from unittest.mock import Mock

import pytest

from modules.sav.application.services.assignment_service import (
    AssignmentService,
)


# ============================================================
# HELPERS
# ============================================================


def make_agent(agent_id: str):
    return Mock(id=agent_id)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def user_repo():
    return Mock()


@pytest.fixture
def ticket_repo():
    return Mock()


@pytest.fixture
def service(user_repo, ticket_repo):
    return AssignmentService(
        user_repository=user_repo,
        ticket_repository=ticket_repo,
    )


# ============================================================
# NO ACTIVE AGENT
# ============================================================


def test_returns_none_when_no_active_agent(
    service,
    user_repo,
    ticket_repo,
):
    user_repo.get_active_agents.return_value = []

    result = service.get_next_agent()

    assert result is None

    user_repo.get_active_agents.assert_called_once_with()

    ticket_repo.count_open_tickets_by_agent.assert_not_called()


# ============================================================
# ONE ACTIVE AGENT
# ============================================================


def test_returns_the_only_active_agent(
    service,
    user_repo,
    ticket_repo,
):
    agent = make_agent("agent-1")

    user_repo.get_active_agents.return_value = [agent]
    ticket_repo.count_open_tickets_by_agent.return_value = 3

    result = service.get_next_agent()

    assert result is agent

    user_repo.get_active_agents.assert_called_once_with()

    ticket_repo.count_open_tickets_by_agent.assert_called_once_with(
        "agent-1"
    )


# ============================================================
# MULTIPLE AGENTS
# ============================================================


def test_returns_agent_with_fewest_open_tickets(
    service,
    user_repo,
    ticket_repo,
):
    agent_1 = make_agent("agent-1")
    agent_2 = make_agent("agent-2")
    agent_3 = make_agent("agent-3")

    user_repo.get_active_agents.return_value = [
        agent_1,
        agent_2,
        agent_3,
    ]

    ticket_counts = {
        "agent-1": 5,
        "agent-2": 2,
        "agent-3": 8,
    }

    def count_open_tickets(agent_id):
        return ticket_counts[agent_id]

    ticket_repo.count_open_tickets_by_agent.side_effect = (
        count_open_tickets
    )

    result = service.get_next_agent()

    assert result is agent_2

    assert ticket_repo.count_open_tickets_by_agent.call_count == 3

    ticket_repo.count_open_tickets_by_agent.assert_any_call(
        "agent-1"
    )
    ticket_repo.count_open_tickets_by_agent.assert_any_call(
        "agent-2"
    )
    ticket_repo.count_open_tickets_by_agent.assert_any_call(
        "agent-3"
    )


# ============================================================
# ZERO TICKETS
# ============================================================


def test_agent_with_zero_open_tickets_is_selected(
    service,
    user_repo,
    ticket_repo,
):
    agent_1 = make_agent("agent-1")
    agent_2 = make_agent("agent-2")

    user_repo.get_active_agents.return_value = [
        agent_1,
        agent_2,
    ]

    ticket_repo.count_open_tickets_by_agent.side_effect = [
        4,
        0,
    ]

    result = service.get_next_agent()

    assert result is agent_2


# ============================================================
# TIE
# ============================================================


def test_first_agent_is_selected_when_ticket_counts_are_equal(
    service,
    user_repo,
    ticket_repo,
):
    agent_1 = make_agent("agent-1")
    agent_2 = make_agent("agent-2")
    agent_3 = make_agent("agent-3")

    user_repo.get_active_agents.return_value = [
        agent_1,
        agent_2,
        agent_3,
    ]

    ticket_repo.count_open_tickets_by_agent.return_value = 3

    result = service.get_next_agent()

    # Le code utilise strictement "<".
    # En cas d'égalité, le premier agent reste sélectionné.
    assert result is agent_1

    assert ticket_repo.count_open_tickets_by_agent.call_count == 3


# ============================================================
# ORDER OF EVALUATION
# ============================================================


def test_all_active_agents_are_evaluated(
    service,
    user_repo,
    ticket_repo,
):
    agents = [
        make_agent("agent-1"),
        make_agent("agent-2"),
        make_agent("agent-3"),
        make_agent("agent-4"),
    ]

    user_repo.get_active_agents.return_value = agents
    ticket_repo.count_open_tickets_by_agent.side_effect = [
        10,
        7,
        4,
        6,
    ]

    result = service.get_next_agent()

    assert result is agents[2]

    assert ticket_repo.count_open_tickets_by_agent.call_args_list == [
        (("agent-1",),),
        (("agent-2",),),
        (("agent-3",),),
        (("agent-4",),),
    ]


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_active_agents_repository_error_is_propagated(
    service,
    user_repo,
    ticket_repo,
):
    user_repo.get_active_agents.side_effect = RuntimeError(
        "user repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="user repository error",
    ):
        service.get_next_agent()

    ticket_repo.count_open_tickets_by_agent.assert_not_called()


def test_ticket_repository_error_is_propagated(
    service,
    user_repo,
    ticket_repo,
):
    agent_1 = make_agent("agent-1")
    agent_2 = make_agent("agent-2")

    user_repo.get_active_agents.return_value = [
        agent_1,
        agent_2,
    ]

    ticket_repo.count_open_tickets_by_agent.side_effect = (
        RuntimeError("ticket repository error")
    )

    with pytest.raises(
        RuntimeError,
        match="ticket repository error",
    ):
        service.get_next_agent()

    ticket_repo.count_open_tickets_by_agent.assert_called_once_with(
        "agent-1"
    )


# ============================================================
# NO WRITE OPERATIONS
# ============================================================


def test_service_does_not_modify_agents_or_tickets(
    service,
    user_repo,
    ticket_repo,
):
    agent_1 = make_agent("agent-1")
    agent_2 = make_agent("agent-2")

    user_repo.get_active_agents.return_value = [
        agent_1,
        agent_2,
    ]

    ticket_repo.count_open_tickets_by_agent.side_effect = [
        2,
        5,
    ]

    result = service.get_next_agent()

    assert result is agent_1

    # Le service ne fait que lire les repositories.
    # Aucun save/update/delete ne doit être nécessaire.
    assert not hasattr(user_repo, "save") or not user_repo.save.called
    assert not hasattr(ticket_repo, "save") or not ticket_repo.save.called