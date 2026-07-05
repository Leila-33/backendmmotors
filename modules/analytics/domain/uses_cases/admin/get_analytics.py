from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from modules.applications.infrastructure.db.application_model import ApplicationModel
from modules.payments.infrastructure.db.payment_model import PaymentModel

class GetAnalyticsUseCase:

    def __init__(self, session):
        self.session = session

    def execute(self):

        # =========================
        # LAST 30 DAYS RANGE
        # =========================
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=30)

        # =========================
        # 1. APPLICATIONS BY DAY
        # =========================
        applications_by_day = (
            self.session.query(
                func.date(ApplicationModel.created_at).label("date"),
                func.count(ApplicationModel.id).label("count")
            )
            .filter(ApplicationModel.created_at >= start_date)
            .group_by(func.date(ApplicationModel.created_at))
            .order_by(func.date(ApplicationModel.created_at))
            .all()
        )

        applications_by_day = [
            {"date": str(row.date), "count": row.count}
            for row in applications_by_day
        ]

        # =========================
        # 2. STATUS DISTRIBUTION
        # =========================
        status_distribution = (
            self.session.query(
                ApplicationModel.status,
                func.count(ApplicationModel.id)
            )
            .group_by(ApplicationModel.status)
            .all()
        )

        status_distribution = [
            {"name": status.value, "value": count}
            for status, count in status_distribution
        ]

        # =========================
        # 3. REVENUE (EXAMPLE SIMULATED)
        # =========================
        revenue = (
        self.session.query(
            func.date_trunc("month", PaymentModel.created_at).label("month"),
            func.sum(PaymentModel.amount).label("amount")
        )
        .filter(PaymentModel.status == "paid")
        .group_by(
            func.date_trunc("month", PaymentModel.created_at)
        )
        .all()
    )

        revenue = [
            {
                "month": row.month.strftime("%Y-%m"),
                "amount": float(row.amount or 0)
            }
            for row in revenue
        ]

        # =========================
        # 4. TOTAL KPIS
        # =========================
        total_applications = self.session.query(ApplicationModel).count()

        approved = self.session.query(ApplicationModel).filter(
            ApplicationModel.status == "approved"
        ).count()

        rejected = self.session.query(ApplicationModel).filter(
            ApplicationModel.status == "rejected"
        ).count()

        submitted = self.session.query(ApplicationModel).filter(
            ApplicationModel.status == "submitted"
        ).count()

        draft = self.session.query(ApplicationModel).filter(
            ApplicationModel.status == "draft"
        ).count()

        # =========================
        # RESPONSE
        # =========================
        return {
            "applications_by_day": applications_by_day,
            "status_distribution": status_distribution,
            "revenue": revenue,
            "stats": {
                "total": total_applications,
                "approved": approved,
                "rejected": rejected,
                "submitted": submitted,
                "draft": draft
            }
        }