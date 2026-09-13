from unittest.mock import Mock

import pytest

from modules.leads.application.dtos.agent.get_lead_detail_dto import (
    GetLeadDetailDTO,
)
from modules.leads.application.results.agent.get_lead_detail_result import (
    GetLeadDetailResult,
)
from modules.leads.application.use_cases.agent.get_lead_detail import (
    GetLeadDetailUseCase,
)
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import LeadNotFound


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def quote_repository():
    return Mock()


@pytest.fixture
def use_case(
    lead_repository,
    quote_repository,
):
    return GetLeadDetailUseCase(
        lead_repository=lead_repository,
        quote_repository=quote_repository,
    )


@pytest.fixture
def dto():
    return GetLeadDetailDTO(
        lead_id="lead-123",
    )


@pytest.fixture
def lead():
    lead = Mock()
    lead.id = "lead-123"
    lead.vehicle_id = "vehicle-123"
    lead.email = "client@example.com"
    lead.status = LeadStatus.NEW

    return lead


def test_execute_returns_lead_detail_successfully(
    use_case,
    lead_repository,
    quote_repository,
    dto,
    lead,
):
    quotes = [
        Mock(id="quote-1"),
        Mock(id="quote-2"),
    ]

    lead_repository.get_by_id_with_details.return_value = lead
    quote_repository.find_summary_by_lead.return_value = quotes
    quote_repository.has_active_quote.return_value = False
    quote_repository.has_any_quote.return_value = False

    result = use_case.execute(dto)

    assert isinstance(result, GetLeadDetailResult)
    assert result.lead is lead
    assert result.quotes == quotes
    assert result.can_create_quote is True
    assert result.can_delete is True

    lead_repository.get_by_id_with_details.assert_called_once_with(
        "lead-123"
    )

    quote_repository.find_summary_by_lead.assert_called_once_with(
        "lead-123"
    )

    quote_repository.has_active_quote.assert_called_once_with(
        "lead-123"
    )

    quote_repository.has_any_quote.assert_called_once_with(
        "lead-123"
    )


def test_execute_raises_when_lead_not_found(
    use_case,
    lead_repository,
    quote_repository,
    dto,
):
    lead_repository.get_by_id_with_details.return_value = None

    with pytest.raises(LeadNotFound):
        use_case.execute(dto)

    lead_repository.get_by_id_with_details.assert_called_once_with(
        "lead-123"
    )

    quote_repository.find_summary_by_lead.assert_not_called()
    quote_repository.has_active_quote.assert_not_called()
    quote_repository.has_any_quote.assert_not_called()


def test_execute_cannot_create_quote_when_active_quote_exists(
    use_case,
    lead_repository,
    quote_repository,
    dto,
    lead,
):
    quotes = [Mock(id="quote-1")]

    lead_repository.get_by_id_with_details.return_value = lead
    quote_repository.find_summary_by_lead.return_value = quotes
    quote_repository.has_active_quote.return_value = True
    quote_repository.has_any_quote.return_value = True

    result = use_case.execute(dto)

    assert result.lead is lead
    assert result.quotes == quotes
    assert result.can_create_quote is False
    assert result.can_delete is False

    quote_repository.has_active_quote.assert_called_once_with(
        "lead-123"
    )

    quote_repository.has_any_quote.assert_called_once_with(
        "lead-123"
    )


@pytest.mark.parametrize(
    "status",
    [
        LeadStatus.WON,
        LeadStatus.LOST,
    ],
)
def test_execute_cannot_delete_non_deletable_status(
    use_case,
    lead_repository,
    quote_repository,
    dto,
    lead,
    status,
):
    lead.status = status

    lead_repository.get_by_id_with_details.return_value = lead
    quote_repository.find_summary_by_lead.return_value = []
    quote_repository.has_active_quote.return_value = False

    result = use_case.execute(dto)

    assert result.can_create_quote is True
    assert result.can_delete is False

    quote_repository.find_summary_by_lead.assert_called_once_with(
        "lead-123"
    )

    quote_repository.has_active_quote.assert_called_once_with(
        "lead-123"
    )

    # Aucun appel inutile : le statut interdit déjà la suppression.
    quote_repository.has_any_quote.assert_not_called()
