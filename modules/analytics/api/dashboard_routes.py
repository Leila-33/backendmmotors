from fastapi import APIRouter, Depends

from modules.analytics.api.schemas import (
    DashboardResponse,
)

from modules.analytics.application.use_cases.get_dashboard import (
    GetDashboardUseCase,
)

from modules.analytics.infrastructure.mappers.dashboard_mapper import (
    DashboardMapper,
)

from modules.analytics.api.dependencies import (
    get_dashboard_use_case,
)

from core.security.dependencies import get_current_user

router = APIRouter(
    tags=["Dashboard"],
)


@router.get(
    "",
    response_model=DashboardResponse,
)
def get_dashboard(
    current_user=Depends(get_current_user),
    use_case: GetDashboardUseCase = Depends(
        get_dashboard_use_case
    ),
):

    result = use_case.execute(
        user_id=current_user.id
    )

    return DashboardMapper.to_response(result)
