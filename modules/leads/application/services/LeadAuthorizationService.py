from modules.leads.domain.exceptions import LeadAccessDenied

class LeadAuthorizationService:


    def check_owner(
        self,
        lead,
        agent_id
    ):

        if lead.assigned_to != agent_id:
            raise LeadAccessDenied()