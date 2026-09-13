from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.application.dtos.agent.agent_lead_dto import AgentLeadDTO
from modules.leads.application.results.agent.mark_lead_contacted_result import (
    MarkLeadContactedResult,
)
from modules.leads.application.use_cases.agent.mark_lead_contacted import (
    MarkLeadContactedUseCase,
)
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import LeadNotFound


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def authorization():
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
    authorization,
    event_service,
    unit_of_work,
):
    return MarkLeadContactedUseCase(
        lead_repository=lead_repository,
        authorization=authorization,
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
    lead.status = LeadStatus.ASSIGNED

    return lead


def test_execute_marks_lead_as_contacted_successfully(
    use_case,
    lead_repository,
    authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead

    # Le Mock ne modifie pas automatiquement le statut.
    lead.mark_as_contacted.side_effect = (
        lambda: setattr(lead, "status", LeadStatus.CONTACTED)
    )

    result = use_case.execute(dto)

    assert isinstance(result, MarkLeadContactedResult)
    assert result.id == "lead-123"
    assert result.status == LeadStatus.CONTACTED.value
    assert result.message == "Prospect marqué comme contacté"

    lead_repository.find_by_id.assert_called_once_with(
        "lead-123"
    )

    authorization.check_owner.assert_called_once_with(
        lead,
        "agent-456",
    )

    lead.mark_as_contacted.assert_called_once_with()

    lead_repository.update.assert_called_once_with(
        lead
    )

    event_service.log.assert_called_once_with(
        type=EventType.LEAD_CONTACTED,
        message="Prospect contacté",
        user_id="agent-456",
        lead_id="lead-123",
        vehicle_id="vehicle-123",
        event_metadata={
            "status": LeadStatus.CONTACTED.value,
        },
    )

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_not_called()


def test_execute_raises_when_lead_not_found(
    use_case,
    lead_repository,
    authorization,
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

    authorization.check_owner.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_authorization_fails(
    use_case,
    lead_repository,
    authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    authorization.check_owner.side_effect = RuntimeError(
        "Accès refusé"
    )

    with pytest.raises(RuntimeError, match="Accès refusé"):
        use_case.execute(dto)

    authorization.check_owner.assert_called_once_with(
        lead,
        "agent-456",
    )

    lead.mark_as_contacted.assert_not_called()
    lead_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_domain_rule_fails(
    use_case,
    lead_repository,
    authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead

    lead.mark_as_contacted.side_effect = RuntimeError(
        "Lead ne peut pas être contacté"
    )

    with pytest.raises(
        RuntimeError,
        match="Lead ne peut pas être contacté",
    ):
        use_case.execute(dto)

    authorization.check_owner.assert_called_once_with(
        lead,
        "agent-456",
    )

    lead.mark_as_contacted.assert_called_once_with()
    lead_repository.update.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_update_fails(
    use_case,
    lead_repository,
    authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead

    lead_repository.update.side_effect = RuntimeError(
        "Erreur de mise à jour"
    )

    with pytest.raises(
        RuntimeError,
        match="Erreur de mise à jour",
    ):
        use_case.execute(dto)

    lead.mark_as_contacted.assert_called_once_with()
    lead_repository.update.assert_called_once_with(
        lead
    )

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_event_fails(
    use_case,
    lead_repository,
    authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead

    lead.mark_as_contacted.side_effect = (
        lambda: setattr(lead, "status", LeadStatus.CONTACTED)
    )

    event_service.log.side_effect = RuntimeError(
        "Erreur événement"
    )

    with pytest.raises(
        RuntimeError,
        match="Erreur événement",
    ):
        use_case.execute(dto)

    lead_repository.update.assert_called_once_with(
        lead
    )

    event_service.log.assert_called_once()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    lead_repository,
    authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead

    lead.mark_as_contacted.side_effect = (
        lambda: setattr(lead, "status", LeadStatus.CONTACTED)
    )

    unit_of_work.commit.side_effect = RuntimeError(
        "Erreur commit"
    )

    with pytest.raises(
        RuntimeError,
        match="Erreur commit",
    ):
        use_case.execute(dto)

    lead_repository.update.assert_called_once_with(
        lead
    )

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_called_once_with()
