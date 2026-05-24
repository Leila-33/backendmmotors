
from fastapi import Depends
from infrastructure.db.dependencies import get_db
from modules.dashboard.application.uses_cases.admin.dashboard import GetDashboardUseCase

def get_dashboard_usecase(
    session = Depends(get_db)
):
    return GetDashboardUseCase(session)