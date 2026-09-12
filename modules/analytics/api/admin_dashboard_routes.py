from fastapi import APIRouter, Depends

from modules.analytics.application.use_cases.admin.get_dashboard import (
    GetAdminDashboardUseCase,
)

from modules.analytics.api.dependencies import (
    get_admin_dashboard_use_case,
)

from modules.analytics.api.schemas import (
    AdminDashboardResponse,
)

from core.security.dependencies import get_current_admin
from modules.analytics.infrastructure.mappers.dashboard_mapper import (
    DashboardMapper,
)
router = APIRouter(tags=["Admin Dashboard"])



@router.get(
    "",
    response_model=AdminDashboardResponse,
)
def get_dashboard(
    use_case: GetAdminDashboardUseCase = Depends(
        get_admin_dashboard_use_case
    ),
    current_admin=Depends(get_current_admin),
):

    result = use_case.execute()

    return DashboardMapper.to_admin_response(result)