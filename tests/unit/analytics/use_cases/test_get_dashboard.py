from unittest.mock import Mock

import pytest

from modules.analytics.application.results.dashboard_result import (
    DashboardResult,
    DashboardApplicationItemResult,
    DashboardTestDriveResult,
    DashboardVehicleResult,
    DashboardNotificationItemResult,
)
from modules.analytics.application.use_cases.get_dashboard import (
    GetDashboardUseCase,
)


def make_dashboard_result():
    return DashboardResult(
        total_applications=10,
        active_applications=4,
        approved_applications=3,
        pending_applications=3,
        applications=[
            DashboardApplicationItemResult(
                id="application-1",
                status="SUBMITTED",
                created_at="2026-09-10T10:00:00+00:00",
            ),
        ],
        upcoming_test_drive=DashboardTestDriveResult(
            id="test-drive-1",
            appointment_date="2026-09-15T14:00:00+00:00",
            status="CONFIRMED",
            vehicle=DashboardVehicleResult(
                id="vehicle-1",
                brand="BMW",
                model="X1",
            ),
        ),
        unread_notifications=2,
        notifications=[
            DashboardNotificationItemResult(
                id="notification-1",
                title="Dossier soumis",
                message="Votre dossier a été soumis.",
                status="UNREAD",
                created_at="2026-09-12T10:00:00+00:00",
            ),
        ],
    )


def test_execute_returns_repository_result():
    dashboard_repository = Mock()

    expected_result = make_dashboard_result()

    dashboard_repository.get_user_dashboard.return_value = expected_result

    use_case = GetDashboardUseCase(
        dashboard_repository=dashboard_repository,
    )

    result = use_case.execute(
        user_id="user-123",
    )

    assert result is expected_result


def test_execute_passes_user_id_to_repository():
    dashboard_repository = Mock()

    dashboard_repository.get_user_dashboard.return_value = (
        make_dashboard_result()
    )

    use_case = GetDashboardUseCase(
        dashboard_repository=dashboard_repository,
    )

    use_case.execute(
        user_id="user-123",
    )

    dashboard_repository.get_user_dashboard.assert_called_once_with(
        user_id="user-123",
    )


def test_execute_propagates_repository_exception():
    dashboard_repository = Mock()

    dashboard_repository.get_user_dashboard.side_effect = RuntimeError(
        "Database error"
    )

    use_case = GetDashboardUseCase(
        dashboard_repository=dashboard_repository,
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(
            user_id="user-123",
        )