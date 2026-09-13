from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

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


def make_statistics():
    return {
        "applications_by_day": [
            {
                "date": "2026-09-01",
                "count": 5,
            },
            {
                "date": "2026-09-02",
                "count": 3,
            },
        ],
        "status_distribution": [
            {
                "name": "SUBMITTED",
                "value": 4,
            },
            {
                "name": "APPROVED",
                "value": 2,
            },
        ],
        "revenue": [
            {
                "month": "2026-08",
                "amount": 15000,
            },
            {
                "month": "2026-09",
                "amount": 8000,
            },
        ],
        "stats": {
            "total": 10,
            "approved": 2,
            "rejected": 1,
            "submitted": 4,
            "draft": 3,
        },
    }


def test_execute_returns_analytics_result():
    analytics_repository = Mock()

    analytics_repository.get_statistics.return_value = make_statistics()

    use_case = GetAnalyticsUseCase(
        analytics_repository=analytics_repository,
    )

    result = use_case.execute()

    assert isinstance(result, AnalyticsResult)

    assert result.applications_by_day == [
        ApplicationByDayResult(
            date="2026-09-01",
            count=5,
        ),
        ApplicationByDayResult(
            date="2026-09-02",
            count=3,
        ),
    ]

    assert result.status_distribution == [
        StatusDistributionResult(
            name="SUBMITTED",
            value=4,
        ),
        StatusDistributionResult(
            name="APPROVED",
            value=2,
        ),
    ]

    assert result.revenue == [
        RevenueByMonthResult(
            month="2026-08",
            amount=15000,
        ),
        RevenueByMonthResult(
            month="2026-09",
            amount=8000,
        ),
    ]

    assert result.stats == AnalyticsStatsResult(
        total=10,
        approved=2,
        rejected=1,
        submitted=4,
        draft=3,
    )


def test_execute_calls_repository_with_last_30_days():
    analytics_repository = Mock()

    analytics_repository.get_statistics.return_value = {
        "applications_by_day": [],
        "status_distribution": [],
        "revenue": [],
        "stats": {
            "total": 0,
            "approved": 0,
            "rejected": 0,
            "submitted": 0,
            "draft": 0,
        },
    }

    use_case = GetAnalyticsUseCase(
        analytics_repository=analytics_repository,
    )

    fixed_now = datetime(
        2026,
        9,
        13,
        12,
        0,
        tzinfo=timezone.utc,
    )

    with patch(
        "modules.analytics.application.use_cases.admin.get_analytics.datetime"
    ) as mocked_datetime:
        mocked_datetime.now.return_value = fixed_now

        use_case.execute()

    analytics_repository.get_statistics.assert_called_once_with(
        start_date=fixed_now - timedelta(days=30),
        end_date=fixed_now,
    )


def test_execute_handles_empty_statistics():
    analytics_repository = Mock()

    analytics_repository.get_statistics.return_value = {
        "applications_by_day": [],
        "status_distribution": [],
        "revenue": [],
        "stats": {
            "total": 0,
            "approved": 0,
            "rejected": 0,
            "submitted": 0,
            "draft": 0,
        },
    }

    use_case = GetAnalyticsUseCase(
        analytics_repository=analytics_repository,
    )

    result = use_case.execute()

    assert result.applications_by_day == []
    assert result.status_distribution == []
    assert result.revenue == []

    assert result.stats == AnalyticsStatsResult(
        total=0,
        approved=0,
        rejected=0,
        submitted=0,
        draft=0,
    )