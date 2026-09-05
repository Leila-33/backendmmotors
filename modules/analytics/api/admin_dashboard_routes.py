from fastapi import APIRouter, Depends

from modules.analytics.application.use_cases.admin.get_dashboard import (
    GetDashboardUseCase,
)

from modules.analytics.api.dependencies import (
    get_dashboard_use_case,
)

from modules.analytics.api.schemas import (
    DashboardResponse,
)

from core.security.dependencies import get_current_admin

router = APIRouter(tags=["Admin Dashboard"])



@router.get(
    "",
    response_model=DashboardResponse,
)
def get_dashboard(
    use_case: GetDashboardUseCase = Depends(
        get_dashboard_use_case
    ),
    current_admin = Depends(get_current_admin)
):

    result = use_case.execute()

    return DashboardResponse(
        stats={
            "total_applications":
                result.stats.total_applications,

            "pending_applications":
                result.stats.pending_applications,

            "active_applications":
                result.stats.active_applications,

            "rejected_applications":
                result.stats.rejected_applications,

            "archived_applications":
                result.stats.archived_applications,

            "applications_this_week":
                result.stats.applications_this_week,
        },

        recent_applications=[
            {
                "id": application.id,
                "status": application.status,
                "first_name": application.first_name,
                "last_name": application.last_name,
                "created_at": application.created_at,
            }
            for application in result.recent_applications
        ],

        recent_events=[
            {
                "id": event.id,
                "type": event.type,
                "message": event.message,
                "created_at": event.created_at,
            }
            for event in result.recent_events
        ],
    )