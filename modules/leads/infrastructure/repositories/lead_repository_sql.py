from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from modules.leads.domain.entities.lead import Lead
from modules.leads.domain.repositories.lead_repository import LeadRepository
from modules.leads.infrastructure.mappers.lead_mapper import LeadMapper
from modules.leads.infrastructure.db.lead_model import LeadModel
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import (
    LeadNotFound
)
from modules.quotes.infrastructure.db.quote_model import QuoteModel
ACTIVE_LEAD_STATUSES = [
    LeadStatus.NEW,
    LeadStatus.CONTACTED,
    LeadStatus.QUOTE_SENT,
    LeadStatus.WON,
]

class LeadRepositorySQL(LeadRepository):

    def __init__(
        self,
        db: Session,
    ):
        self.db = db


    # =====================================
    # CREATE
    # =====================================

    def save(
        self,
        lead: Lead,
    ) -> None:

        model = LeadMapper.to_model(
            lead
        )

        self.db.add(model)


    # =====================================
    # UPDATE
    # =====================================

    def update(
        self,
        lead: Lead,
    ) -> None:

        model = (
            self.db.query(LeadModel)
            .filter(
                LeadModel.id == lead.id
            )
            .first()
        )

        if model is None:
            return

        LeadMapper.update_model(
            model,
            lead,
        )


    # =====================================
    # FIND BY ID
    # =====================================

    def find_by_id(
        self,
        lead_id: str,
    ) -> Lead | None:

        model = (
            self.db.query(LeadModel)
            .filter(
                LeadModel.id == lead_id
            )
            .first()
        )

        if not model:
            return None

        return LeadMapper.to_domain(
            model
        )


    # =====================================
    # FIND BY ID WITH DETAILS
    # =====================================

    def get_by_id_with_details(
    self,
    lead_id: str,
) -> Lead | None:

        model = (
            self.db.query(LeadModel)
            .options(
                joinedload(
                    LeadModel.vehicle
                ),
                joinedload(
                    LeadModel.assigned_agent
                ),
            )
            .filter(
                LeadModel.id == lead_id
            )
            .first()
        )

        if model is None:
            return None

        return LeadMapper.to_domain(
            model
        )
    
    


    # =====================================
    # AGENT LEADS
    # =====================================

    def find_my_leads(
        self,
        agent_id: str,
    ) -> list[Lead]:

        models = (
            self.db.query(LeadModel)
            .options(
                joinedload(
                    LeadModel.vehicle
                )
            )
            .filter(
                LeadModel.assigned_to == agent_id
            )
            .order_by(
                LeadModel.created_at.desc()
            )
            .all()
        )

        return [
            LeadMapper.to_domain(
                model
            )
            for model in models
        ]
    

    # =====================================
    # UNASSIGNED LEADS
    # =====================================

    def find_unassigned_leads(
        self,
    ) -> list[Lead]:

        models = (
            self.db.query(LeadModel)
            .options(
                joinedload(
                    LeadModel.vehicle
                )
            )
            .filter(
                LeadModel.assigned_to.is_(None)
            )
            .order_by(
                LeadModel.created_at.desc()
            )
            .all()
        )

        return [
            LeadMapper.to_domain(
                model
            )
            for model in models
        ]
    

    def find_active_by_user_or_email_and_vehicle(
        self,
        user_id: str | None,
        email: str,
        vehicle_id: str,
    ) -> Lead | None:

        conditions = [
            LeadModel.email == email,
        ]

        if user_id:
            conditions.append(
                LeadModel.user_id == user_id
            )


        model = (
            self.db
            .query(LeadModel)
            .filter(
                LeadModel.vehicle_id == vehicle_id,
                LeadModel.status.in_(
                    ACTIVE_LEAD_STATUSES
                ),
                or_(*conditions)
            )
            .order_by(
                LeadModel.created_at.desc()
            )
            .first()
        )


        if not model:
            return None


        return LeadMapper.to_domain(
            model
        )



    def find_active_by_user_and_vehicle(
        self,
        user_id: str,
        vehicle_id: str,
    ) -> Lead | None:

        model = (
            self.db
            .query(LeadModel)
            .filter(
                LeadModel.user_id == user_id,
                LeadModel.vehicle_id == vehicle_id,
                LeadModel.status.in_(
                    ACTIVE_LEAD_STATUSES
                )
            )
            .order_by(
                LeadModel.created_at.desc()
            )
            .first()
        )


        if not model:
            return None


        return LeadMapper.to_domain(
            model
        )



    def attach_user(
        self,
        lead_id: str,
        user_id: str,
    ) -> None:

        lead = (
            self.db
            .query(LeadModel)
            .filter(
                LeadModel.id == lead_id
            )
            .first()
        )

        if not lead:
            return


        lead.user_id = user_id

    def delete(
    self,
    lead_id: str,
):

        model = (
            self.db.query(LeadModel)
            .filter(
                LeadModel.id == lead_id
            )
            .first()
        )


        if model is None:
            raise LeadNotFound()


        self.db.delete(
            model
        )


    def get_by_quote_id(
        self,
        quote_id: str,
    ):
        return (
            self.db.query(LeadModel)
            .join(
                QuoteModel,
                QuoteModel.lead_id == LeadModel.id,
            )
            .filter(
                QuoteModel.id == quote_id
            )
            .first()
        )