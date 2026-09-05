from fastapi import APIRouter, Depends
from core.security.dependencies import get_current_admin

from modules.analytics.application.use_cases.admin.get_analytics import (
    GetAnalyticsUseCase,
)

from modules.analytics.api.schemas import (
    AnalyticsResponse,
)

from modules.analytics.api.dependencies import (
    get_analytics_usecase,
)

router = APIRouter(tags=["AdminAnalytics"])


@router.get(
    "",
    response_model=AnalyticsResponse,
)
def get_analytics(
    use_case: GetAnalyticsUseCase = Depends(
        get_analytics_usecase
    ),
    current_admin = Depends(get_current_admin)

):

    result = use_case.execute()

    return AnalyticsResponse(
        applications_by_day=[
            {
                "date": item.date,
                "count": item.count,
            }
            for item in result.applications_by_day
        ],

        status_distribution=[
            {
                "name": item.name,
                "value": item.value,
            }
            for item in result.status_distribution
        ],

        revenue=[
            {
                "month": item.month,
                "amount": item.amount,
            }
            for item in result.revenue
        ],

        stats={
            "total": result.stats.total,
            "approved": result.stats.approved,
            "rejected": result.stats.rejected,
            "submitted": result.stats.submitted,
            "draft": result.stats.draft,
        },
    )

