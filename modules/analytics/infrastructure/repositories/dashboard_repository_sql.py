from datetime import datetime, timedelta, timezone

from modules.analytics.domain.repositories.dashboard_repository import (
    DashboardRepository,
)

from modules.applications.domain.enums import (
    ApplicationStatus,
)
from modules.applications.infrastructure.db.application_model import (
    ApplicationModel,
)

from modules.applications.infrastructure.db.event_model import (
    EventModel,
)


class DashboardRepositorySQL(DashboardRepository):

    def __init__(self, session):
        self.session = session

    def get_dashboard_data(self) -> dict:

        # =========================
        # TOTAL APPLICATIONS
        # =========================

        total_applications = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.deleted_at.is_(None)
            )
            .count()
        )

        # =========================
        # PENDING APPLICATIONS
        # =========================

        pending_applications = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.status
                == ApplicationStatus.SUBMITTED,
                ApplicationModel.deleted_at.is_(None),
            )
            .count()
        )

        # =========================
        # APPROVED APPLICATIONS
        # =========================

        active_applications = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.status.in_(
                    [
                        ApplicationStatus.APPROVED,
                        ApplicationStatus.PAID,
                        ApplicationStatus.COMPLETED,
                    ]
                ),
                ApplicationModel.deleted_at.is_(None),
            )
            .count()
        )
        # =========================
        # REJECTED APPLICATIONS
        # =========================

        rejected_applications = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.status
                == ApplicationStatus.REJECTED,
                ApplicationModel.deleted_at.is_(None),
            )
            .count()
        )

        # =========================
        # ARCHIVED APPLICATIONS
        # =========================

        archived_applications = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.is_archived.is_(True),
                ApplicationModel.deleted_at.is_(None),
            )
            .count()
        )

        # =========================
        # LAST 7 DAYS
        # =========================

        now = datetime.now(timezone.utc)

        last_week = now - timedelta(days=7)

        applications_this_week = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.created_at >= last_week,
                ApplicationModel.created_at <= now,
                ApplicationModel.deleted_at.is_(None),
            )
            .count()
        )

        # =========================
        # RECENT APPLICATIONS
        # =========================

        recent_applications = (
            self.session.query(ApplicationModel)
            .filter(
                ApplicationModel.deleted_at.is_(None)
            )
            .order_by(
                ApplicationModel.created_at.desc()
            )
            .limit(5)
            .all()
        )

        recent_applications = [
            {
                "id": application.id,
                "status": application.status.value,
                "first_name": application.first_name,
                "last_name": application.last_name,
                "created_at": application.created_at,
            }
            for application in recent_applications
        ]

        # =========================
        # RECENT EVENTS
        # =========================

        recent_events = (
            self.session.query(EventModel)
            .order_by(
                EventModel.created_at.desc()
            )
            .limit(10)
            .all()
        )

        recent_events = [
            {
                "id": event.id,
                "type": (
                    event.type.value
                    if hasattr(event.type, "value")
                    else event.type
                ),
                "message": event.message,
                "created_at": event.created_at,
            }
            for event in recent_events
        ]

        # =========================
        # RESULT
        # =========================

        return {
            "stats": {
                "total_applications": total_applications,
                "pending_applications": pending_applications,
                "active_applications": active_applications,
                "rejected_applications": rejected_applications,
                "archived_applications": archived_applications,
                "applications_this_week": applications_this_week,
            },
            "recent_applications": recent_applications,
            "recent_events": recent_events,
        }