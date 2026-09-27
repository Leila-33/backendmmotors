from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from modules.analytics.application.results.admin.analytics_result import (
    AnalyticsResult,
    ApplicationByDayResult,
    StatusDistributionResult,
    RevenueByMonthResult,
    AnalyticsStatsResult,
)
from modules.analytics.application.use_cases.admin.get_analytics import (
    GetAnalyticsUseCase,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def analytics_repository():
    return Mock()


@pytest.fixture
def use_case(
    analytics_repository,
):
    return GetAnalyticsUseCase(
        analytics_repository=analytics_repository,
    )


@pytest.fixture
def statistics():
    return {
        "applications_by_day": [
            {
                "date": "2026-09-25",
                "count": 5,
            },
            {
                "date": "2026-09-26",
                "count": 8,
            },
        ],
        "status_distribution": [
            {
                "name": "DRAFT",
                "value": 4,
            },
            {
                "name": "SUBMITTED",
                "value": 6,
            },
            {
                "name": "APPROVED",
                "value": 3,
            },
        ],
        "revenue": [
            {
                "month": "2026-08",
                "amount": 15000,
            },
            {
                "month": "2026-09",
                "amount": 22000,
            },
        ],
        "stats": {
            "total": 13,
            "active": 9,
            "rejected": 1,
            "submitted": 6,
            "draft": 4,
        },
    }


# ============================================================
# BASIC EXECUTION
# ============================================================


def test_execute_returns_analytics_result(
    use_case,
    analytics_repository,
    statistics,
):
    analytics_repository.get_statistics.return_value = statistics

    result = use_case.execute()

    assert isinstance(
        result,
        AnalyticsResult,
    )


# ============================================================
# APPLICATIONS BY DAY
# ============================================================


def test_execute_maps_applications_by_day(
    use_case,
    analytics_repository,
    statistics,
):
    analytics_repository.get_statistics.return_value = statistics

    result = use_case.execute()

    assert result.applications_by_day == [
        ApplicationByDayResult(
            date="2026-09-25",
            count=5,
        ),
        ApplicationByDayResult(
            date="2026-09-26",
            count=8,
        ),
    ]


def test_execute_preserves_application_day_order(
    use_case,
    analytics_repository,
    statistics,
):
    analytics_repository.get_statistics.return_value = statistics

    result = use_case.execute()

    assert result.applications_by_day[0].date == "2026-09-25"
    assert result.applications_by_day[1].date == "2026-09-26"

    assert result.applications_by_day[0].count == 5
    assert result.applications_by_day[1].count == 8


# ============================================================
# STATUS DISTRIBUTION
# ============================================================


def test_execute_maps_status_distribution(
    use_case,
    analytics_repository,
    statistics,
):
    analytics_repository.get_statistics.return_value = statistics

    result = use_case.execute()

    assert result.status_distribution == [
        StatusDistributionResult(
            name="DRAFT",
            value=4,
        ),
        StatusDistributionResult(
            name="SUBMITTED",
            value=6,
        ),
        StatusDistributionResult(
            name="APPROVED",
            value=3,
        ),
    ]


# ============================================================
# REVENUE
# ============================================================


def test_execute_maps_revenue(
    use_case,
    analytics_repository,
    statistics,
):
    analytics_repository.get_statistics.return_value = statistics

    result = use_case.execute()

    assert result.revenue == [
        RevenueByMonthResult(
            month="2026-08",
            amount=15000,
        ),
        RevenueByMonthResult(
            month="2026-09",
            amount=22000,
        ),
    ]


# ============================================================
# STATS
# ============================================================


def test_execute_maps_statistics(
    use_case,
    analytics_repository,
    statistics,
):
    analytics_repository.get_statistics.return_value = statistics

    result = use_case.execute()

    assert result.stats == AnalyticsStatsResult(
        total=13,
        active=9,
        rejected=1,
        submitted=6,
        draft=4,
    )


# ============================================================
# COMPLETE RESULT
# ============================================================


def test_execute_maps_complete_result(
    use_case,
    analytics_repository,
    statistics,
):
    analytics_repository.get_statistics.return_value = statistics

    result = use_case.execute()

    assert result.applications_by_day[0].date == "2026-09-25"
    assert result.applications_by_day[0].count == 5

    assert result.status_distribution[0].name == "DRAFT"
    assert result.status_distribution[0].value == 4

    assert result.revenue[0].month == "2026-08"
    assert result.revenue[0].amount == 15000

    assert result.stats.total == 13
    assert result.stats.active == 9
    assert result.stats.rejected == 1
    assert result.stats.submitted == 6
    assert result.stats.draft == 4


# ============================================================
# DATE RANGE
# ============================================================


def test_execute_requests_last_30_days(
    use_case,
    analytics_repository,
    statistics,
):
    analytics_repository.get_statistics.return_value = statistics

    before = datetime.now(timezone.utc)

    use_case.execute()

    after = datetime.now(timezone.utc)

    analytics_repository.get_statistics.assert_called_once()

    kwargs = (
        analytics_repository
        .get_statistics
        .call_args.kwargs
    )

    start_date = kwargs["start_date"]
    end_date = kwargs["end_date"]

    assert start_date.tzinfo == timezone.utc
    assert end_date.tzinfo == timezone.utc

    assert timedelta(days=29, seconds=59) <= (
        end_date - start_date
    ) <= timedelta(days=30, seconds=1)

    assert before <= end_date <= after


# ============================================================
# REPOSITORY CALL
# ============================================================


def test_execute_calls_repository_once(
    use_case,
    analytics_repository,
    statistics,
):
    analytics_repository.get_statistics.return_value = statistics

    use_case.execute()

    analytics_repository.get_statistics.assert_called_once()


# ============================================================
# EMPTY DATA
# ============================================================


def test_execute_handles_empty_statistics(
    use_case,
    analytics_repository,
):
    analytics_repository.get_statistics.return_value = {
        "applications_by_day": [],
        "status_distribution": [],
        "revenue": [],
        "stats": {
            "total": 0,
            "active": 0,
            "rejected": 0,
            "submitted": 0,
            "draft": 0,
        },
    }

    result = use_case.execute()

    assert isinstance(
        result,
        AnalyticsResult,
    )

    assert result.applications_by_day == []
    assert result.status_distribution == []
    assert result.revenue == []

    assert result.stats.total == 0
    assert result.stats.active == 0
    assert result.stats.rejected == 0
    assert result.stats.submitted == 0
    assert result.stats.draft == 0


# ============================================================
# REPOSITORY ERROR
# ============================================================


def test_execute_propagates_repository_error(
    use_case,
    analytics_repository,
):
    analytics_repository.get_statistics.side_effect = (
        RuntimeError("analytics repository error")
    )

    with pytest.raises(
        RuntimeError,
        match="analytics repository error",
    ):
        use_case.execute()

    analytics_repository.get_statistics.assert_called_once()