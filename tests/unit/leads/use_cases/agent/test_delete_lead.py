from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.application.dtos.agent.agent_lead_dto import AgentLeadDTO
from modules.leads.application.results.agent.delete_lead_result import (
    DeleteLeadResult,
)
from modules.leads.application.use_cases.agent.delete_lead import (
    DeleteLeadUseCase,
)
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import (
    LeadCannotBeDeleted,
    LeadNotFound,
)


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def quote_repository():
    return Mock()


@pytest.fixture
def lead_authorization():
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
    quote_repository,
    lead_authorization,
    event_service,
    unit_of_work,
):
    return DeleteLeadUseCase(
        lead_repository=lead_repository,
        quote_repository=quote_repository,
        lead_authorization=lead_authorization,
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
    lead.email = "client@example.com"
    lead.status = LeadStatus.NEW

    return lead


def test_execute_deletes_lead_successfully(
    use_case,
    lead_repository,
    quote_repository,
    lead_authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    quote_repository.has_any_quote.return_value = False

    result = use_case.execute(dto)

    assert isinstance(result, DeleteLeadResult)
    assert result.lead_id == "lead-123"
    assert result.message == "Lead supprimé avec succès."

    lead_repository.find_by_id.assert_called_once_with(
        "lead-123"
    )

    lead_authorization.check_owner.assert_called_once_with(
        lead,
        "agent-456",
    )

    quote_repository.has_any_quote.assert_called_once_with(
        "lead-123"
    )

    lead_repository.delete.assert_called_once_with(
        "lead-123"
    )

    event_service.log.assert_called_once_with(
        type=EventType.LEAD_DELETED,
        message="Lead supprimé",
        user_id="agent-456",
        lead_id="lead-123",
        vehicle_id="vehicle-123",
        event_metadata={
            "email": "client@example.com",
            "status": LeadStatus.NEW.value,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_execute_raises_when_lead_not_found(
    use_case,
    lead_repository,
    quote_repository,
    lead_authorization,
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

    lead_authorization.check_owner.assert_not_called()
    quote_repository.has_any_quote.assert_not_called()
    lead_repository.delete.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_authorization_fails(
    use_case,
    lead_repository,
    quote_repository,
    lead_authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    lead_authorization.check_owner.side_effect = RuntimeError(
        "Unauthorized"
    )

    with pytest.raises(
        RuntimeError,
        match="Unauthorized",
    ):
        use_case.execute(dto)

    lead_authorization.check_owner.assert_called_once_with(
        lead,
        "agent-456",
    )

    quote_repository.has_any_quote.assert_not_called()
    lead_repository.delete.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


@pytest.mark.parametrize(
    "status",
    [
        LeadStatus.WON,
        LeadStatus.LOST,
    ],
)
def test_execute_rejects_non_deletable_status(
    use_case,
    lead_repository,
    quote_repository,
    lead_authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
    status,
):
    lead_repository.find_by_id.return_value = lead
    lead.status = status

    with pytest.raises(LeadCannotBeDeleted):
        use_case.execute(dto)

    lead_authorization.check_owner.assert_called_once_with(
        lead,
        "agent-456",
    )

    quote_repository.has_any_quote.assert_not_called()
    lead_repository.delete.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


def test_execute_rejects_lead_with_existing_quote(
    use_case,
    lead_repository,
    quote_repository,
    lead_authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    quote_repository.has_any_quote.return_value = True

    with pytest.raises(LeadCannotBeDeleted):
        use_case.execute(dto)

    lead_authorization.check_owner.assert_called_once_with(
        lead,
        "agent-456",
    )

    quote_repository.has_any_quote.assert_called_once_with(
        "lead-123"
    )

    lead_repository.delete.assert_not_called()
    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_delete_fails(
    use_case,
    lead_repository,
    quote_repository,
    lead_authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    quote_repository.has_any_quote.return_value = False
    lead_repository.delete.side_effect = RuntimeError(
        "Delete error"
    )

    with pytest.raises(
        RuntimeError,
        match="Delete error",
    ):
        use_case.execute(dto)

    lead_repository.delete.assert_called_once_with(
        "lead-123"
    )

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_event_logging_fails(
    use_case,
    lead_repository,
    quote_repository,
    lead_authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    quote_repository.has_any_quote.return_value = False
    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        use_case.execute(dto)

    lead_repository.delete.assert_called_once_with(
        "lead-123"
    )

    event_service.log.assert_called_once()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    lead_repository,
    quote_repository,
    lead_authorization,
    event_service,
    unit_of_work,
    dto,
    lead,
):
    lead_repository.find_by_id.return_value = lead
    quote_repository.has_any_quote.return_value = False
    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(dto)

    lead_repository.delete.assert_called_once_with(
        "lead-123"
    )

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()