from modules.analytics.application.results.admin.dashboard_result import (
    DashboardResult,
    DashboardStatsResult,
    RecentApplicationResult,
    RecentEventResult,
)


class GetDashboardUseCase:

    def __init__(self, dashboard_repository):
        self.dashboard_repository = dashboard_repository

    def execute(self) -> DashboardResult:

        result = self.dashboard_repository.get_dashboard_data()

        return DashboardResult(
            stats=DashboardStatsResult(
                total_applications=result["stats"]["total_applications"],
                pending_applications=result["stats"]["pending_applications"],
                active_applications=result["stats"]["active_applications"],
                rejected_applications=result["stats"]["rejected_applications"],
                archived_applications=result["stats"]["archived_applications"],
                applications_this_week=result["stats"][
                    "applications_this_week"
                ],
            ),

            recent_applications=[
                RecentApplicationResult(
                    id=application["id"],
                    status=application["status"],
                    first_name=application["first_name"],
                    last_name=application["last_name"],
                    created_at=application["created_at"],
                )
                for application in result["recent_applications"]
            ],

            recent_events=[
                RecentEventResult(
                    id=event["id"],
                    type=event["type"],
                    message=event["message"],
                    created_at=event["created_at"],
                )
                for event in result["recent_events"]
            ],
        )