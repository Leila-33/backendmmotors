from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.application.dtos.agent.agent_lead_dto import AgentLeadDTO
from modules.leads.application.results.agent.assign_lead_result import (
    AssignLeadResult,
)
from modules.leads.application.use_cases.agent.assign_lead import (
    AssignLeadUseCase,
)
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import LeadNotFound


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    lead_repository,
    event_service,
    unit_of_work,
):
    return AssignLeadUseCase(
        lead_repository=lead_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return AgentLeadDTO(
        lead_id="lead-123",
        agent_id="agent-456",
    )


@pytest.fixture
def lead():
    lead = Mock()
    lead.id = "lead-123"
    lead.vehicle_id = "vehicle-123"
    lead.status = LeadStatus.NEW
    lead.assigned_to = None

    return lead


def test_execute_assigns_lead_successfully(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead

    def assign_to(agent_id):
        lead.assigned_to = agent_id
        lead.status = LeadStatus.ASSIGNED

    lead.assign_to.side_effect = assign_to

    result = use_case.execute(dto)

    assert isinstance(result, AssignLeadResult)
    assert result.id == "lead-123"
    assert result.status == LeadStatus.ASSIGNED.value
    assert result.assigned_to == "agent-456"
    assert result.message == "Lead assigné"

    lead_repository.find_by_id.assert_called_once_with(
        "lead-123",
    )

    lead.ensure_assignable.assert_called_once()

    lead.assign_to.assert_called_once_with(
        "agent-456",
    )

    lead_repository.update.assert_called_once_with(
        lead,
    )

    event_service.log.assert_called_once_with(
        type=EventType.LEAD_ASSIGNED,
        message="Lead assigné à un agent",
        user_id="agent-456",
        lead_id="lead-123",
        vehicle_id="vehicle-123",
        event_metadata={
            "assigned_to": "agent-456",
            "status": LeadStatus.ASSIGNED.value,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_execute_raises_when_lead_not_found(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
):
    lead_repository.find_by_id.return_value = None

    with pytest.raises(LeadNotFound):
        use_case.execute(dto)

    lead_repository.find_by_id.assert_called_once_with(
        "lead-123"
    )

    lead_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_lead_is_not_assignable(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    lead.ensure_assignable.side_effect = RuntimeError(
        "Lead cannot be assigned"
    )

    with pytest.raises(
        RuntimeError,
        match="Lead cannot be assigned",
    ):
        use_case.execute(dto)

    lead.ensure_assignable.assert_called_once()
    lead.assign_to.assert_not_called()

    lead_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_update_fails(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    lead_repository.update.side_effect = RuntimeError(
        "Update error"
    )

    with pytest.raises(
        RuntimeError,
        match="Update error",
    ):
        use_case.execute(dto)

    lead.ensure_assignable.assert_called_once()
    lead.assign_to.assert_called_once_with(
        "agent-456"
    )

    lead_repository.update.assert_called_once_with(
        lead
    )

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_event_logging_fails(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        use_case.execute(dto)

    lead_repository.update.assert_called_once_with(
        lead
    )
    event_service.log.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    lead_repository,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(dto)

    lead_repository.update.assert_called_once_with(
        lead
    )
    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()