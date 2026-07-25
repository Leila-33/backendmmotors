from datetime import datetime, timedelta, timezone

from modules.applications.domain.enums import ApplicationStatus


from modules.applications.infrastructure.db.application_model import (
    ApplicationModel
)

from modules.applications.infrastructure.db.event_model import (
    EventModel
)

class GetDashboardUseCase:

    def __init__(self, session):
        self.session = session

    def execute(self):

        # =========================
        # TOTALS
        # =========================
        total_applications = (
            self.session.query(
                ApplicationModel
            ).count()
        )

        pending_applications = (
            self.session.query(
                ApplicationModel
            )
            .filter(
                ApplicationModel.status ==
                ApplicationStatus.SUBMITTED
            )
            .count()
        )

        approved_applications = (
            self.session.query(
                ApplicationModel
            )
            .filter(
                ApplicationModel.status ==
                ApplicationStatus.APPROVED
            )
            .count()
        )

        rejected_applications = (
            self.session.query(
                ApplicationModel
            )
            .filter(
                ApplicationModel.status ==
                ApplicationStatus.REJECTED
            )
            .count()
        )

        archived_applications = (
            self.session.query(
                ApplicationModel
            )
            .filter(
                ApplicationModel.is_archived == True
            )
            .count()
        )

        # =========================
        # LAST 7 DAYS
        # =========================
        last_week = (
            datetime.now(timezone.utc)
            - timedelta(days=7)
        )

        applications_this_week = (
            self.session.query(
                ApplicationModel
            )
            .filter(
                ApplicationModel.created_at >= last_week
            )
            .count()
        )

        # =========================
        # RECENT APPLICATIONS
        # =========================
        recent_applications = (
            self.session.query(
                ApplicationModel
            )
            .order_by(
                ApplicationModel.created_at.desc()
            )
            .limit(5)
            .all()
        )

        recent_applications = [
            {
                "id": app.id,
                "status": app.status.value,
                "first_name": app.first_name,
                "last_name": app.last_name,
                "created_at": app.created_at
            }
            for app in recent_applications
        ]

        # =========================
        # RECENT EVENTS
        # =========================
        recent_events = (
            self.session.query(
                EventModel
            )
            .order_by(
                EventModel.created_at.desc()
            )
            .limit(10)
            .all()
        )

        recent_events = [
            {
                "id": event.id,
                "type": event.type,
                "message": event.message,
                "created_at": event.created_at
            }
            for event in recent_events
        ]

        # =========================
        # RESPONSE
        # =========================
        return {

            "stats": {

                "total_applications":
                    total_applications,

                "pending_applications":
                    pending_applications,

                "approved_applications":
                    approved_applications,

                "rejected_applications":
                    rejected_applications,

                "archived_applications":
                    archived_applications,

                "applications_this_week":
                    applications_this_week
            },

            "recent_applications":
                recent_applications,

            "recent_events":
                recent_events
        }