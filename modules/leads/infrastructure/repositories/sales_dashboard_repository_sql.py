from sqlalchemy import func
from sqlalchemy.orm import Session

from modules.leads.domain.enums import LeadStatus
from modules.leads.application.results.agent.sales_notification_counts_result import (
    SalesNotificationCountsResult,
)
from modules.leads.application.results.agent.get_sales_dashboard_statistics_result import (
    SalesDashboardStatisticsResult,
)

from modules.leads.infrastructure.db.lead_model import LeadModel
from modules.quotes.infrastructure.db.quote_model import QuoteModel
from modules.applications.infrastructure.db.application_model import (
    ApplicationModel,
)

from modules.leads.domain.repositories.sales_dashboard_repository import (
    SalesDashboardRepository,
)


class SalesDashboardRepositorySQL(
    SalesDashboardRepository
):

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    # =====================================================
    # STATISTICS
    # =====================================================

    def get_statistics(
        self,
        agent_id: str,
    ) -> SalesDashboardStatisticsResult:

        # =================================================
        # LEADS
        # =================================================

        new_leads = (
            self.db.query(func.count(LeadModel.id))
            .filter(
                LeadModel.status == LeadStatus.NEW,
            )
            .scalar()
            or 0
        )

        my_leads = (
            self.db.query(func.count(LeadModel.id))
            .filter(
                LeadModel.assigned_to == agent_id,
            )
            .scalar()
            or 0
        )

        unassigned = (
            self.db.query(func.count(LeadModel.id))
            .filter(
                LeadModel.assigned_to.is_(None),
            )
            .scalar()
            or 0
        )

        won = (
            self.db.query(func.count(LeadModel.id))
            .filter(
                LeadModel.assigned_to == agent_id,
                LeadModel.status == LeadStatus.WON,
            )
            .scalar()
            or 0
        )

        lost = (
            self.db.query(func.count(LeadModel.id))
            .filter(
                LeadModel.assigned_to == agent_id,
                LeadModel.status == LeadStatus.LOST,
            )
            .scalar()
            or 0
        )

        # =================================================
        # QUOTES
        # =================================================

        quotes_sent = (
            self.db.query(func.count(QuoteModel.id))
            .join(
                LeadModel,
                LeadModel.id == QuoteModel.lead_id,
            )
            .filter(
                LeadModel.assigned_to == agent_id,
                QuoteModel.sent_at.isnot(None),
            )
            .scalar()
            or 0
        )

        # =================================================
        # APPLICATIONS
        # =================================================

        applications = (
            self.db.query(func.count(ApplicationModel.id))
            .join(
                QuoteModel,
                QuoteModel.id == ApplicationModel.quote_id,
            )
            .join(
                LeadModel,
                LeadModel.id == QuoteModel.lead_id,
            )
            .filter(
                LeadModel.assigned_to == agent_id,
                ApplicationModel.deleted_at.is_(None),
                ApplicationModel.is_archived.is_(False),
            )
            .scalar()
            or 0
        )

        # =================================================
        # CONVERSION RATE
        # =================================================

        total_closed = won + lost

        conversion_rate = (
            (won / total_closed) * 100
            if total_closed > 0
            else 0.0
        )

        # =================================================
        # RESULT
        # =================================================

        return SalesDashboardStatisticsResult(
            new_leads=new_leads,
            my_leads=my_leads,
            quotes_sent=quotes_sent,
            applications=applications,
            unassigned=unassigned,
            won=won,
            lost=lost,
            conversion_rate=conversion_rate,
        )

    def get_notification_counts(
        self,
        agent_id: str,
    ) -> SalesNotificationCountsResult:

        # =====================================================
        # NOUVEAUX LEADS
        # =====================================================

        new_leads_count = (
            self.db.query(func.count(LeadModel.id))
            .filter(
                LeadModel.status == LeadStatus.NEW,
                LeadModel.assigned_to.is_(None),
            )
            .scalar()
            or 0
        )

        # =====================================================
        # MES LEADS À TRAITER
        # =====================================================

        my_leads_count = (
            self.db.query(func.count(LeadModel.id))
            .filter(
                LeadModel.assigned_to == agent_id,
                LeadModel.status.notin_(
                    [
                        LeadStatus.WON,
                        LeadStatus.LOST
                    ]
                ),
            )
            .scalar()
            or 0
        )

        return SalesNotificationCountsResult(
            new_leads_count=new_leads_count,
            my_leads_count=my_leads_count,
        )