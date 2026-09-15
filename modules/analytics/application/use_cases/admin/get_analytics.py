from datetime import datetime, timedelta, timezone

from modules.analytics.application.results.admin.analytics_result import (
    AnalyticsResult,
    ApplicationByDayResult,
    StatusDistributionResult,
    RevenueByMonthResult,
    AnalyticsStatsResult,
)


class GetAnalyticsUseCase:

    def __init__(
        self,
        analytics_repository,
    ):
        self.analytics_repository = analytics_repository

    def execute(self) -> AnalyticsResult:

        now = datetime.now(timezone.utc)

        start_date = now - timedelta(days=30)

        result = self.analytics_repository.get_statistics(
            start_date=start_date,
            end_date=now,
        )

        return AnalyticsResult(

            applications_by_day=[
                ApplicationByDayResult(
                    date=item["date"],
                    count=item["count"],
                )
                for item in result["applications_by_day"]
            ],

            status_distribution=[
                StatusDistributionResult(
                    name=item["name"],
                    value=item["value"],
                )
                for item in result["status_distribution"]
            ],

            revenue=[
                RevenueByMonthResult(
                    month=item["month"],
                    amount=item["amount"],
                )
                for item in result["revenue"]
            ],

            stats=AnalyticsStatsResult(
                total=result["stats"]["total"],
                active=result["stats"]["active"],
                rejected=result["stats"]["rejected"],
                submitted=result["stats"]["submitted"],
                draft=result["stats"]["draft"],
            ),
        )

