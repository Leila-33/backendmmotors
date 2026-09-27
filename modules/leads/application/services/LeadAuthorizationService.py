from modules.leads.domain.exceptions import LeadAccessDenied

class LeadAuthorizationService:

    """
    Vérifie qu'un agent est autorisé à effectuer une action
    sur un lead qui lui est attribué.
    """
    def check_owner(
        self,
        lead,
        agent_id
    ):

        if lead.assigned_to != agent_id:
            raise LeadAccessDenied()