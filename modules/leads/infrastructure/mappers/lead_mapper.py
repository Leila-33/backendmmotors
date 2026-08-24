from modules.leads.domain.entities.lead import Lead
from modules.leads.infrastructure.db.lead_model import LeadModel
from modules.vehicles.infrastructure.mappers.vehicle_mapper import VehicleMapper
from modules.auth.infrastructure.mappers.user_mapper import UserMapper
from modules.leads.application.results.agent.get_lead_detail_result import GetLeadDetailResult
from modules.leads.application.results.agent.get_sales_leads_result import GetSalesLeadsResult
class LeadMapper:

    # =====================================================
    # DB → DOMAIN
    # =====================================================
    @staticmethod
    def to_domain(model: LeadModel) -> Lead:
        return Lead(
            id=model.id,
            vehicle_id=model.vehicle_id,
            user_id=model.user_id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone=model.phone,
            message=model.message,

            status=model.status,
            assigned_to=model.assigned_to,

            created_at=model.created_at,
            vehicle=(
    VehicleMapper.to_domain(
        model.vehicle
    )
)
if model.vehicle
else None,
            assigned_agent=(
    UserMapper.to_domain(
        model.assigned_agent
    )
)
if model.assigned_agent
else None)
           

        

    # =====================================================
    # DOMAIN → DB (CREATE)
    # =====================================================
    @staticmethod
    def to_model(domain: Lead) -> LeadModel:
        return LeadModel(
            id=domain.id,
            vehicle_id=domain.vehicle_id,
            user_id=domain.user_id,
            first_name=domain.first_name,
            last_name=domain.last_name,
            email=domain.email,
            phone=domain.phone,
            message=domain.message,

            status=domain.status,
            assigned_to=domain.assigned_to,

            created_at=domain.created_at,
        )

    # =====================================================
    # UPDATE EXISTING MODEL (IMPORTANT)
    # =====================================================
    @staticmethod
    def update_model(model: LeadModel, lead: Lead) -> LeadModel:

        model.vehicle_id = lead.vehicle_id

        model.first_name = lead.first_name
        model.last_name = lead.last_name
        model.email = lead.email
        model.phone = lead.phone
        model.message = lead.message

        model.status = lead.status
        model.assigned_to = lead.assigned_to

        # timestamps
        model.created_at = lead.created_at

        return model
    
    @staticmethod
    def to_response(lead):

        return {
            "id": lead.id,

            "first_name": lead.first_name,
            "last_name": lead.last_name,

            "status": (
                lead.status.value
                if hasattr(lead.status, "value")
                else lead.status
            ),

            "vehicle": (
                {
                    "id": lead.vehicle.id,
                    "brand": lead.vehicle.brand,
                    "model": lead.vehicle.model,
                    "price": lead.vehicle.price,
                }
                if lead.vehicle
                else None
            ),

            "created_at": lead.created_at,
        }
    
    @staticmethod
    def to_detail_response(
        result: GetLeadDetailResult
    ):
        lead = result.lead
        quotes = result.quotes
        return {

            "id": lead.id,

            "first_name": lead.first_name,

            "last_name": lead.last_name,

            "email": lead.email,

            "phone": lead.phone,

            "message": lead.message,


            "status": (
                lead.status.value
                if hasattr(
                    lead.status,
                    "value"
                )
                else lead.status
            ),


            "vehicle": (
                {
                    "id": lead.vehicle.id,
                    "brand": lead.vehicle.brand,
                    "model": lead.vehicle.model,
                    "price": lead.vehicle.price,
                }
                if lead.vehicle
                else None
            ),


            "assigned_agent": (
                {
                    "id": lead.assigned_agent.id,
                    "first_name": lead.assigned_agent.first_name,
                    "last_name": lead.assigned_agent.last_name,
                }
                if lead.assigned_agent
                else None
            ),


            "quotes": [
                {
                    "id": quote.id,
                    "status": (
                        quote.status.value
                        if hasattr(
                            quote.status,
                            "value"
                        )
                        else quote.status
                    ),
                }
                for quote in quotes
            ],


            "created_at": lead.created_at,
            "can_create_quote": result.can_create_quote,
            "can_delete": result.can_delete
        }

    @staticmethod
    def to_list_response(
        result: GetSalesLeadsResult,
    ):
        return [
            LeadMapper.to_response(lead)
            for lead in result.leads
        ]