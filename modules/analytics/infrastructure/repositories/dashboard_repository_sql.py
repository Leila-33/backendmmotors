from datetime import datetime, timedelta, timezone
from sqlalchemy import func

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

from modules.test_drives.infrastructure.db.test_drive_model import (
    TestDriveModel,
)
from modules.test_drives.domain.enums import (
    TestDriveStatus,
)
from modules.notifications.infrastructure.db.notification_model import (
    NotificationModel,
)
from modules.notifications.domain.enums import (
    NotificationStatus,
)
from modules.analytics.application.results.dashboard_result import (
    DashboardResult,
    DashboardApplicationItemResult,
    DashboardTestDriveResult,
    DashboardNotificationItemResult,
    DashboardVehicleResult,
)

class DashboardRepositorySQL(DashboardRepository):

    def __init__(self, session):
        self.session = session
# =========================================================
# ADMIN DASHBOARD DATA
# =========================================================
    def get_admin_dashboard_data(self) -> dict:

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

 
# =========================================================
# USER DASHBOARD DATA
# =========================================================
    def get_user_dashboard(
        self,
        user_id: str,
    ) -> DashboardResult:

        # =====================================================
        # DOSSIERS
        # =====================================================

        # Nombre total de dossiers non supprimés
        total_applications = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.user_id == user_id,
                ApplicationModel.deleted_at.is_(None),
            )
            .count()
        )

        # Nombre de dossiers actifs
        #
        # Un dossier est considéré comme actif lorsqu'il est :
        # - approuvé
        # - payé
        # - terminé
        active_applications = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.user_id == user_id,
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

        # Nombre de dossiers en attente
        pending_applications = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.user_id == user_id,
                ApplicationModel.status
                == ApplicationStatus.SUBMITTED,
                ApplicationModel.deleted_at.is_(None),
            )
            .count()
        )

        # Nombre de dossiers approuvés
        approved_applications = (
            self.session.query(ApplicationModel.id)
            .filter(
                ApplicationModel.user_id == user_id,
                ApplicationModel.status
                == ApplicationStatus.APPROVED,
                ApplicationModel.deleted_at.is_(None),
            )
            .count()
        )

        # Les 3 derniers dossiers
        applications = (
            self.session.query(ApplicationModel)
            .filter(
                ApplicationModel.user_id == user_id,
                ApplicationModel.deleted_at.is_(None),
            )
            .order_by(
                ApplicationModel.created_at.desc()
            )
            .limit(3)
            .all()
        )

        application_items = [
            DashboardApplicationItemResult(
                id=str(application.id),
                status=application.status,
                created_at=application.created_at,
            )
            for application in applications
        ]

        # =====================================================
        # PROCHAIN ESSAI
        # =====================================================

        upcoming_test_drive = (
            self.session.query(TestDriveModel)
            .filter(
                TestDriveModel.user_id == user_id,
                TestDriveModel.status == TestDriveStatus.CONFIRMED,
                TestDriveModel.appointment_date > func.now(),
            )
            .order_by(
                TestDriveModel.appointment_date.asc()
            )
            .first()
        )

        upcoming_test_drive_result = None

        if upcoming_test_drive:

            upcoming_test_drive_result = DashboardTestDriveResult(
                id=str(upcoming_test_drive.id),
                appointment_date=upcoming_test_drive.appointment_date,
                status=upcoming_test_drive.status,
                vehicle=DashboardVehicleResult(
                    id=str(upcoming_test_drive.vehicle.id),
                    brand=upcoming_test_drive.vehicle.brand,
                    model=upcoming_test_drive.vehicle.model,
                ),
            )

        # =====================================================
        # NOTIFICATIONS
        # =====================================================

        # Nombre de notifications non lues
        unread_notifications = (
            self.session.query(NotificationModel.id)
            .filter(
                NotificationModel.user_id == user_id,
                NotificationModel.status == NotificationStatus.UNREAD,
            )
            .count()
        )

        # Les 5 dernières notifications
        notifications = (
            self.session.query(NotificationModel)
            .filter(
                NotificationModel.user_id == user_id,
            )
            .order_by(
                NotificationModel.created_at.desc()
            )
            .limit(5)
            .all()
        )

        notification_items = [
            DashboardNotificationItemResult(
                id=str(notification.id),
                title=notification.title,
                message=notification.message,
                status=notification.status,
                created_at=notification.created_at,
            )
            for notification in notifications
        ]

        # =====================================================
        # RESULT
        # =====================================================

        return DashboardResult(
            total_applications=total_applications,
            active_applications=active_applications,
            approved_applications=approved_applications,
            pending_applications=pending_applications,
            applications=application_items,
            upcoming_test_drive=upcoming_test_drive_result,
            unread_notifications=unread_notifications,
            notifications=notification_items,
        )
