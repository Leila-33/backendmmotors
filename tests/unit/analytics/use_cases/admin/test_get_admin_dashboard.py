from unittest.mock import Mock

from modules.analytics.application.results.admin.admin_dashboard_result import (
    AdminDashboardResult,
    DashboardStatsResult,
    RecentApplicationResult,
    RecentEventResult,
)
from modules.analytics.application.use_cases.admin.get_dashboard import (
    GetAdminDashboardUseCase,
)


def make_dashboard_data():
    return {
        "stats": {
            "total_applications": 20,
            "pending_applications": 5,
            "active_applications": 8,
            "rejected_applications": 2,
            "archived_applications": 5,
            "applications_this_week": 4,
        },
        "recent_applications": [
            {
                "id": "application-1",
                "status": "SUBMITTED",
                "first_name": "Leila",
                "last_name": "El",
                "created_at": "2026-09-10T10:00:00+00:00",
            },
            {
                "id": "application-2",
                "status": "APPROVED",
                "first_name": "Jean",
                "last_name": "Dupont",
                "created_at": "2026-09-11T14:30:00+00:00",
            },
        ],
        "recent_events": [
            {
                "id": "event-1",
                "type": "APPLICATION_CREATED",
                "message": "Dossier créé.",
                "created_at": "2026-09-10T10:00:00+00:00",
            },
            {
                "id": "event-2",
                "type": "APPLICATION_SUBMITTED",
                "message": "Dossier soumis.",
                "created_at": "2026-09-11T14:30:00+00:00",
            },
        ],
    }


def test_execute_returns_admin_dashboard_result():
    dashboard_repository = Mock()

    dashboard_repository.get_admin_dashboard_data.return_value = (
        make_dashboard_data()
    )

    use_case = GetAdminDashboardUseCase(
        dashboard_repository=dashboard_repository,
    )

    result = use_case.execute()

    assert isinstance(result, AdminDashboardResult)

    assert result.stats == DashboardStatsResult(
        total_applications=20,
        pending_applications=5,
        active_applications=8,
        rejected_applications=2,
        archived_applications=5,
        applications_this_week=4,
    )

    assert result.recent_applications == [
        RecentApplicationResult(
            id="application-1",
            status="SUBMITTED",
            first_name="Leila",
            last_name="El",
            created_at="2026-09-10T10:00:00+00:00",
        ),
        RecentApplicationResult(
            id="application-2",
            status="APPROVED",
            first_name="Jean",
            last_name="Dupont",
            created_at="2026-09-11T14:30:00+00:00",
        ),
    ]

    assert result.recent_events == [
        RecentEventResult(
            id="event-1",
            type="APPLICATION_CREATED",
            message="Dossier créé.",
            created_at="2026-09-10T10:00:00+00:00",
        ),
        RecentEventResult(
            id="event-2",
            type="APPLICATION_SUBMITTED",
            message="Dossier soumis.",
            created_at="2026-09-11T14:30:00+00:00",
        ),
    ]


def test_execute_calls_repository_once():
    dashboard_repository = Mock()

    dashboard_repository.get_admin_dashboard_data.return_value = (
        make_dashboard_data()
    )

    use_case = GetAdminDashboardUseCase(
        dashboard_repository=dashboard_repository,
    )

    use_case.execute()

    dashboard_repository.get_admin_dashboard_data.assert_called_once_with()


def test_execute_handles_empty_recent_data():
    dashboard_repository = Mock()

    dashboard_repository.get_admin_dashboard_data.return_value = {
        "stats": {
            "total_applications": 0,
            "pending_applications": 0,
            "active_applications": 0,
            "rejected_applications": 0,
            "archived_applications": 0,
            "applications_this_week": 0,
        },
        "recent_applications": [],
        "recent_events": [],
    }

    use_case = GetAdminDashboardUseCase(
        dashboard_repository=dashboard_repository,
    )

    result = use_case.execute()

    assert isinstance(result, AdminDashboardResult)

    assert result.recent_applications == []
    assert result.recent_events == []

    assert result.stats == DashboardStatsResult(
        total_applications=0,
        pending_applications=0,
        active_applications=0,
        rejected_applications=0,
        archived_applications=0,
        applications_this_week=0,
    )