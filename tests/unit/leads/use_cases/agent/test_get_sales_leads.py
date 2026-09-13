from unittest.mock import Mock

import pytest

from modules.leads.application.dtos.agent.get_sales_leads_dto import (
    GetSalesLeadsDTO,
)
from modules.leads.application.results.agent.get_sales_leads_result import (
    GetSalesLeadsResult,
)
from modules.leads.application.use_cases.agent.get_sales_leads import (
    GetSalesLeadsUseCase,
)


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def use_case(lead_repository):
    return GetSalesLeadsUseCase(
        lead_repository=lead_repository,
    )


def test_execute_returns_my_leads(
    use_case,
    lead_repository,
):
    dto = GetSalesLeadsDTO(
        user_id="agent-123",
        scope="my",
    )

    leads = [
        Mock(id="lead-1"),
        Mock(id="lead-2"),
    ]

    lead_repository.find_my_leads.return_value = leads

    result = use_case.execute(dto)

    assert isinstance(result, GetSalesLeadsResult)
    assert result.leads == leads

    lead_repository.find_my_leads.assert_called_once_with(
        "agent-123"
    )

    lead_repository.find_unassigned_leads.assert_not_called()


def test_execute_returns_unassigned_leads(
    use_case,
    lead_repository,
):
    dto = GetSalesLeadsDTO(
        user_id="agent-123",
        scope="unassigned",
    )

    leads = [
        Mock(id="lead-1"),
        Mock(id="lead-2"),
    ]

    lead_repository.find_unassigned_leads.return_value = leads

    result = use_case.execute(dto)

    assert isinstance(result, GetSalesLeadsResult)
    assert result.leads == leads

    lead_repository.find_unassigned_leads.assert_called_once_with()

    lead_repository.find_my_leads.assert_not_called()


def test_execute_returns_empty_list_when_repository_returns_no_leads(
    use_case,
    lead_repository,
):
    dto = GetSalesLeadsDTO(
        user_id="agent-123",
        scope="my",
    )

    lead_repository.find_my_leads.return_value = []

    result = use_case.execute(dto)

    assert isinstance(result, GetSalesLeadsResult)
    assert result.leads == []

    lead_repository.find_my_leads.assert_called_once_with(
        "agent-123"
    )