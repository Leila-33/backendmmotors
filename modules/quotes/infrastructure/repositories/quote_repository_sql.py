from sqlalchemy.orm import joinedload
from modules.quotes.domain.repositories.quote_repository import QuoteRepository
from modules.quotes.domain.enums import QuoteStatus
from modules.quotes.infrastructure.db.quote_model import QuoteModel
from modules.leads.infrastructure.db.lead_model import LeadModel
from modules.quotes.infrastructure.mappers.quote_mapper import QuoteMapper
from datetime import datetime, timezone
from sqlalchemy import case

class QuoteRepositorySQL(QuoteRepository):

    def __init__(self, db):
        self.db = db

    # =====================================
    # CREATE
    # =====================================

    def save(self, quote):

        model = QuoteMapper.to_model(
            quote
        )

        self.db.add(model)

        return quote

    # =====================================
    # UPDATE
    # =====================================

    def update(self, quote):

        model = (
            self.db.query(QuoteModel)
            .filter(
                QuoteModel.id == quote.id
            )
            .first()
        )

        if model is None:
            return

        QuoteMapper.update_model(
            model,
            quote,
        )

    # =====================================
    # FIND BY LEAD
    # =====================================

    def find_by_lead(
        self,
        lead_id: str,
    ):

        models = (
            self.db.query(QuoteModel)
            .filter(
                QuoteModel.lead_id == lead_id
            )
            .order_by(
                QuoteModel.created_at.desc()
            )
            .all()
        )

        return [
            QuoteMapper.to_domain(model)
            for model in models
        ]

    # =====================================
    # ACTIVE QUOTE
    # =====================================

    def find_active_by_lead(
        self,
        lead_id: str,
    ):

        model = (
            self.db.query(QuoteModel)
            .filter(
                QuoteModel.lead_id == lead_id,
                QuoteModel.status.in_([
                    QuoteStatus.DRAFT,
                    QuoteStatus.SENT,
                    QuoteStatus.ACCEPTED,
                ])
            )
            .order_by(
                QuoteModel.created_at.desc()
            )
            .first()
        )

        if model is None:
            return None

        return QuoteMapper.to_domain(
            model
        )

    # =====================================
    # MY QUOTES
    # =====================================

    def find_by_sales_agent(
        self,
        sales_agent_id: str,
    ):

        models = (
            self.db.query(QuoteModel)
            .join(
                LeadModel,
                LeadModel.id == QuoteModel.lead_id
            )
            .options(
                joinedload(
                    QuoteModel.lead
                )
                .joinedload(
                    LeadModel.vehicle
                ),

                joinedload(
                    QuoteModel.lead
                )
                .joinedload(
                    LeadModel.assigned_agent
                ),
            )
            .filter(
                LeadModel.assigned_to == sales_agent_id
            )
            .order_by(
                QuoteModel.created_at.desc()
            )
            .all()
        )


        return [
            QuoteMapper.to_domain(model)
            for model in models
        ]

    # =====================================
    # CUSTOMER QUOTES
    # =====================================

    def find_by_customer(
        self,
        customer_id: str,
    ):

        status_order = case(
            {
                QuoteStatus.SENT: 1,
                QuoteStatus.ACCEPTED: 2,
                QuoteStatus.REJECTED: 3,
                QuoteStatus.EXPIRED: 4,
            },
            value=QuoteModel.status,
        )


        models = (
            self.db.query(QuoteModel)
            .join(QuoteModel.lead)
            .options(
                joinedload(
                    QuoteModel.lead
                ).joinedload(
                    LeadModel.vehicle
                ),

                joinedload(
                    QuoteModel.lead
                ).joinedload(
                    LeadModel.assigned_agent
                ),

                joinedload(
                    QuoteModel.trade_in
                ),
            )
            .filter(
                LeadModel.user_id == customer_id,

                QuoteModel.status.in_([
                    QuoteStatus.SENT,
                    QuoteStatus.ACCEPTED,
                    QuoteStatus.REJECTED,
                    QuoteStatus.EXPIRED
                ])
            )
            .order_by(
                status_order,
                QuoteModel.created_at.desc()
            )
            .all()
        )


        return [
            QuoteMapper.to_domain(model)
            for model in models
        ]

    # =====================================
    # CUSTOMER QUOTE DETAIL
    # =====================================

    def find_customer_quote_by_id(
    self,
    quote_id: str,
    customer_id: str,
):

        model = (
            self.db.query(QuoteModel)
            .join(QuoteModel.lead)
            .options(
                joinedload(
                    QuoteModel.lead
                ).joinedload(
                    LeadModel.vehicle
                ),

                joinedload(
                    QuoteModel.lead
                ).joinedload(
                    LeadModel.assigned_agent
                ),

                joinedload(
                    QuoteModel.trade_in
                ),
            )
            .filter(
                QuoteModel.id == quote_id,
                LeadModel.user_id == customer_id,
            )
            .first()
        )

        if model is None:
            return None

        return QuoteMapper.to_domain(
            model
        )
    # =====================================
    # AGENT QUOTE DETAIL
    # =====================================
    def find_by_id(
    self,
    quote_id: str,
):

        model = (
            self.db
            .query(QuoteModel)
            .options(
                joinedload(
                    QuoteModel.lead
                ).joinedload(
                    LeadModel.vehicle
                ),

                joinedload(
                    QuoteModel.lead
                ).joinedload(
                    LeadModel.assigned_agent
                ),

                joinedload(
                    QuoteModel.trade_in
                ),
            )
            .filter(
                QuoteModel.id == quote_id
            )
            .first()
        )


        if model is None:
            return None


        return QuoteMapper.to_domain(
            model
    )
    # =====================================
    # ACTION REQUIRED COUNT
    # =====================================

    def count_action_required_by_customer(
        self,
        user_id: str,
    ):

        return (
            self.db.query(QuoteModel)
            .join(
                LeadModel,
                LeadModel.id == QuoteModel.lead_id,
            )
            .filter(
                LeadModel.user_id == user_id,
                QuoteModel.status == QuoteStatus.SENT,
            )
            .count()
        )
    
    def find_summary_by_lead(
    self,
    lead_id: str,
):

        return (
            self.db
            .query(
                QuoteModel.id,
                QuoteModel.status,
            )
            .filter(
                QuoteModel.lead_id == lead_id
            )
            .order_by(
                QuoteModel.created_at.desc()
            )
            .all()
        )
    
    def has_active_quote(
    self,
    lead_id: str,
):

        return (
            self.db.query(QuoteModel)
            .filter(
                QuoteModel.lead_id == lead_id,
                QuoteModel.status.in_([
                    QuoteStatus.DRAFT,
                    QuoteStatus.SENT,
                    QuoteStatus.ACCEPTED,
                ])
            )
            .first()
            is not None
        )

    def find_quotes_to_expire(
        self,
    ):

        models = (
            self.db.query(QuoteModel)
            .filter(
                QuoteModel.status == QuoteStatus.SENT,
                QuoteModel.expires_at <= datetime.now(timezone.utc)
            )
            .all()
        )


        return [
            QuoteMapper.to_domain(model)
            for model in models
        ]

    def delete(
    self,
    quote_id: str,
):

        model = (
            self.db.query(QuoteModel)
            .filter(
                QuoteModel.id == quote_id
            )
            .first()
        )


        if model:

            self.db.delete(model)
    
    def has_any_quote(
    self,
    lead_id: str,
) -> bool:

        return (
            self.db.query(QuoteModel.id)
            .filter(
                QuoteModel.lead_id == lead_id
            )
            .first()
            is not None
        )