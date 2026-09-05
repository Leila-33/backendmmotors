from datetime import datetime

from sqlalchemy import func

from modules.analytics.domain.repositories.analytics_repository import (
    AnalyticsRepository,
)

from modules.applications.domain.enums import (
    ApplicationStatus,
)

from modules.applications.infrastructure.db.application_model import (
    ApplicationModel,
)

from modules.payments.domain.enums import (
    PaymentStatus,
)

from modules.financing.domain.enums import (
    InstallmentStatus,
)

from modules.payments.infrastructure.db.payment_model import (
    PaymentModel,
)

from modules.financing.infrastructure.db.installment_model import (
    InstallmentPaymentModel,
)


class AnalyticsRepositorySQL(AnalyticsRepository):

    def __init__(self, session):
        self.session = session

    def get_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:

        # =========================================
        # 1. APPLICATIONS BY DAY
        # =========================================

        applications_by_day = (
            self.session.query(
                func.date(
                    ApplicationModel.created_at
                ).label("date"),

                func.count(
                    ApplicationModel.id
                ).label("count"),
            )
            .filter(
                ApplicationModel.created_at >= start_date,
                ApplicationModel.created_at <= end_date,
            )
            .group_by(
                func.date(
                    ApplicationModel.created_at
                )
            )
            .order_by(
                func.date(
                    ApplicationModel.created_at
                )
            )
            .all()
        )

        applications_by_day = [
            {
                "date": str(row.date),
                "count": row.count,
            }
            for row in applications_by_day
        ]

        # =========================================
        # 2. STATUS DISTRIBUTION
        # =========================================

        status_distribution = (
            self.session.query(
                ApplicationModel.status,
                func.count(
                    ApplicationModel.id
                ).label("count"),
            )
            .group_by(
                ApplicationModel.status
            )
            .all()
        )

        status_distribution = [
            {
                "name": status.value,
                "value": count,
            }
            for status, count in status_distribution
        ]

        # =========================================
        # 3. REVENUE FROM INITIAL PAYMENTS
        # =========================================

        payments_revenue = (
            self.session.query(
                func.date_trunc(
                    "month",
                    PaymentModel.paid_at,
                ).label("month"),

                func.sum(
                    PaymentModel.amount
                ).label("amount"),
            )
            .filter(
                PaymentModel.paid_at >= start_date,
                PaymentModel.paid_at <= end_date,
                PaymentModel.status == PaymentStatus.PAID,
            )
            .group_by(
                func.date_trunc(
                    "month",
                    PaymentModel.paid_at,
                )
            )
            .order_by(
                func.date_trunc(
                    "month",
                    PaymentModel.paid_at,
                )
            )
            .all()
        )

        # =========================================
        # 4. REVENUE FROM INSTALLMENTS
        # =========================================

        installments_revenue = (
            self.session.query(
                func.date_trunc(
                    "month",
                    InstallmentPaymentModel.paid_at,
                ).label("month"),

                func.sum(
                    InstallmentPaymentModel.amount
                ).label("amount"),
            )
            .filter(
                InstallmentPaymentModel.paid_at >= start_date,
                InstallmentPaymentModel.paid_at <= end_date,
                InstallmentPaymentModel.status
                == InstallmentStatus.PAID,
            )
            .group_by(
                func.date_trunc(
                    "month",
                    InstallmentPaymentModel.paid_at,
                )
            )
            .order_by(
                func.date_trunc(
                    "month",
                    InstallmentPaymentModel.paid_at,
                )
            )
            .all()
        )

        # =========================================
        # 5. MERGE REVENUES
        # =========================================

        revenue_by_month = {}

        # Initial payments

        for row in payments_revenue:

            month = row.month.strftime("%Y-%m")

            revenue_by_month[month] = (
                revenue_by_month.get(month, 0)
                + float(row.amount or 0)
            )

        # Installments

        for row in installments_revenue:

            month = row.month.strftime("%Y-%m")

            revenue_by_month[month] = (
                revenue_by_month.get(month, 0)
                + float(row.amount or 0)
            )

        revenue = [
            {
                "month": month,
                "amount": amount,
            }
            for month, amount
            in sorted(revenue_by_month.items())
        ]

        # =========================================
        # 6. TOTAL APPLICATIONS
        # =========================================

        total_applications = (
            self.session.query(
                ApplicationModel.id
            )
            .count()
        )

        # =========================================
        # 7. APPROVED APPLICATIONS
        # =========================================

        approved = (
            self.session.query(
                ApplicationModel.id
            )
            .filter(
                ApplicationModel.status
                == ApplicationStatus.APPROVED
            )
            .count()
        )

        # =========================================
        # 8. REJECTED APPLICATIONS
        # =========================================

        rejected = (
            self.session.query(
                ApplicationModel.id
            )
            .filter(
                ApplicationModel.status
                == ApplicationStatus.REJECTED
            )
            .count()
        )

        # =========================================
        # 9. SUBMITTED APPLICATIONS
        # =========================================

        submitted = (
            self.session.query(
                ApplicationModel.id
            )
            .filter(
                ApplicationModel.status
                == ApplicationStatus.SUBMITTED
            )
            .count()
        )

        # =========================================
        # 10. DRAFT APPLICATIONS
        # =========================================

        draft = (
            self.session.query(
                ApplicationModel.id
            )
            .filter(
                ApplicationModel.status
                == ApplicationStatus.DRAFT
            )
            .count()
        )

        # =========================================
        # 11. RETURN STATISTICS
        # =========================================

        return {
            "applications_by_day": applications_by_day,

            "status_distribution": status_distribution,

            "revenue": revenue,

            "stats": {
                "total": total_applications,
                "approved": approved,
                "rejected": rejected,
                "submitted": submitted,
                "draft": draft,
            },
        }


