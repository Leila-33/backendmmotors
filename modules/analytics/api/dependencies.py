from modules.analytics.domain.uses_cases.admin.get_analytics import GetAnalyticsUseCase
from fastapi import Depends
from core.database.dependencies import get_db

def get_analytics_usecase(session = Depends(get_db)):
    return GetAnalyticsUseCase(session)
