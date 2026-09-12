from fastapi import Depends
from modules.analytics.application.use_cases.admin.get_analytics import GetAnalyticsUseCase
from modules.analytics.infrastructure.repositories.analytics_repository_sql import (
    AnalyticsRepository,
)
from modules.analytics.application.use_cases.admin.get_dashboard import (
        GetAdminDashboardUseCase,
    )
from modules.analytics.application.use_cases.get_dashboard import (
    GetDashboardUseCase,
)
from modules.dependencies.dependencies import (
    get_analytics_repository,
    get_dashboard_repository,
)
# =========================================================
# ADMIN
# =========================================================
def get_analytics_usecase(
    analytics_repository: AnalyticsRepository = Depends(
        get_analytics_repository
    )
):

    return GetAnalyticsUseCase(
        analytics_repository=analytics_repository
    )
def get_admin_dashboard_use_case(
    dashboard_repository = Depends(get_dashboard_repository)
):
    return GetAdminDashboardUseCase(
        dashboard_repository=dashboard_repository
    )

# =========================================================
# USER
# =========================================================
def get_dashboard_use_case(
    dashboard_repository = Depends(get_dashboard_repository)
):
    return GetDashboardUseCase(
        dashboard_repository=dashboard_repository
    )