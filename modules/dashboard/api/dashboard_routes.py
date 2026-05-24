from fastapi import APIRouter, Depends

from modules.dashboard.application.uses_cases.admin.dashboard import (
    GetDashboardUseCase
)

from modules.dashboard.api.dependencies import (
    get_dashboard_usecase
)
from core.security.dependencies import get_current_admin

router = APIRouter(tags=["Admin Dashboard"])


@router.get("")
def get_dashboard(
    usecase: GetDashboardUseCase = Depends(
        get_dashboard_usecase
    ),
    current_admin = Depends(get_current_admin)
):
    return usecase.execute()