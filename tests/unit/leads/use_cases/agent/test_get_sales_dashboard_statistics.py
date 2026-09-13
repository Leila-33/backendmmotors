from unittest.mock import Mock

import pytest

from modules.leads.application.dtos.agent.agent_dto import AgentDTO
from modules.leads.application.results.agent.get_sales_dashboard_statistics_result import (
    SalesDashboardStatisticsResult,
)
from modules.leads.application.use_cases.agent.get_sales_dashboard_statistics import (
    GetSalesDashboardStatisticsUseCase,
)


@pytest.fixture
def sales_dashboard_repository():
    return Mock()


@pytest.fixture
def use_case(sales_dashboard_repository):
    return GetSalesDashboardStatisticsUseCase(
        sales_dashboard_repository=sales_dashboard_repository,
    )


@pytest.fixture
def dto():
    return AgentDTO(
        agent_id="agent-123",
    )


def test_execute_returns_dashboard_statistics(
    use_case,
    sales_dashboard_repository,
    dto,
):
    statistics = SalesDashboardStatisticsResult(
        new_leads=5,
        my_leads=12,
        quotes_sent=8,
        applications=4,
        unassigned=3,
        won=6,
        lost=2,
        conversion_rate=50.0,
    )

    sales_dashboard_repository.get_statistics.return_value = statistics

    result = use_case.execute(dto)

    assert result is statistics

    sales_dashboard_repository.get_statistics.assert_called_once_with(
        agent_id="agent-123",
    )


def test_execute_propagates_repository_exception(
    use_case,
    sales_dashboard_repository,
    dto,
):
    sales_dashboard_repository.get_statistics.side_effect = RuntimeError(
        "Erreur repository"
    )

    with pytest.raises(RuntimeError, match="Erreur repository"):
        use_case.execute(dto)

    sales_dashboard_repository.get_statistics.assert_called_once_with(
        agent_id="agent-123",
    )
