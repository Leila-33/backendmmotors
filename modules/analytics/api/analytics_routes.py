
from modules.analytics.domain.uses_cases.admin.get_analytics import GetAnalyticsUseCase
from core.security.dependencies import get_current_admin
from fastapi import APIRouter, Depends

router = APIRouter(tags=["AdminAnalytics"])
from modules.analytics.api.dependencies import get_analytics_usecase

@router.get("")
def get_admin_analytics(
    usecase: GetAnalyticsUseCase = Depends(get_analytics_usecase),
    current_admin = Depends(get_current_admin)
):
    return usecase.execute()