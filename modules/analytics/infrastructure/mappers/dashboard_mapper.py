from modules.analytics.api.schemas import (
    DashboardResponse,
    DashboardApplicationResponse,
    DashboardTestDriveResponse,
    DashboardNotificationResponse,
)
from modules.analytics.application.results.admin.admin_dashboard_result import (
    AdminDashboardResult,
)
from modules.analytics.api.schemas import (
    AdminDashboardResponse,
)

class DashboardMapper:

    @staticmethod
    def to_response(result):

        return DashboardResponse(
            total_applications=result.total_applications,
            active_applications=result.active_applications,
            approved_applications=result.approved_applications,
            pending_applications=result.pending_applications,

            applications=[
                DashboardApplicationResponse(
                    id=application.id,
                    status=application.status,
                    created_at=application.created_at,
                )
                for application in result.applications
            ],

            upcoming_test_drive=(
                DashboardTestDriveResponse(
                    id=result.upcoming_test_drive.id,
                    appointment_date=(
                        result.upcoming_test_drive
                        .appointment_date
                    ),
                    status=result.upcoming_test_drive.status,
                )
                if result.upcoming_test_drive
                else None
            ),

            unread_notifications=(
                result.unread_notifications
            ),

            notifications=[
                DashboardNotificationResponse(
                    id=notification.id,
                    title=notification.title,
                    message=notification.message,
                    status=notification.status,
                    created_at=notification.created_at,
                )
                for notification in result.notifications
            ],
        )





    @staticmethod
    def to_admin_response(
        result: AdminDashboardResult,
    ) -> AdminDashboardResponse:

        return AdminDashboardResponse(
            stats={
                "total_applications": result.stats.total_applications,
                "pending_applications": result.stats.pending_applications,
                "active_applications": result.stats.active_applications,
                "rejected_applications": result.stats.rejected_applications,
                "archived_applications": result.stats.archived_applications,
                "applications_this_week": result.stats.applications_this_week,
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