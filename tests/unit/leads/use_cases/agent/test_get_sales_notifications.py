from unittest.mock import Mock

import pytest

from modules.leads.application.dtos.agent.agent_dto import AgentDTO
from modules.leads.application.results.agent.sales_notification_counts_result import (
    SalesNotificationCountsResult,
)
from modules.leads.application.use_cases.agent.get_sales_notifications import (
    GetSalesNotificationsUseCase,
)


@pytest.fixture
def sales_dashboard_repository():
    return Mock()


@pytest.fixture
def use_case(sales_dashboard_repository):
    return GetSalesNotificationsUseCase(
        sales_dashboard_repository=sales_dashboard_repository,
    )


@pytest.fixture
def dto():
    return AgentDTO(
        agent_id="agent-123",
    )


def test_execute_returns_notification_counts(
    use_case,
    sales_dashboard_repository,
    dto,
):
    expected_result = SalesNotificationCountsResult(
        new_leads_count=5,
        my_leads_count=3,
    )

    sales_dashboard_repository.get_notification_counts.return_value = (
        expected_result
    )

    result = use_case.execute(dto)

    assert result is expected_result

    sales_dashboard_repository.get_notification_counts.assert_called_once_with(
        agent_id="agent-123",
    )


def test_execute_returns_zero_counts(
    use_case,
    sales_dashboard_repository,
    dto,
):
    expected_result = SalesNotificationCountsResult(
        new_leads_count=0,
        my_leads_count=0,
    )

    sales_dashboard_repository.get_notification_counts.return_value = (
        expected_result
    )

    result = use_case.execute(dto)

    assert result is expected_result

    sales_dashboard_repository.get_notification_counts.assert_called_once_with(
        agent_id="agent-123",
    )


def test_execute_propagates_repository_error(
    use_case,
    sales_dashboard_repository,
    dto,
):
    sales_dashboard_repository.get_notification_counts.side_effect = (
        RuntimeError("Database error")
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    sales_dashboard_repository.get_notification_counts.assert_called_once_with(
        agent_id="agent-123",
    )
