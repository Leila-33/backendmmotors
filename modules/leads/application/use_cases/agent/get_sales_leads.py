from modules.leads.infrastructure.mappers.lead_mapper import LeadMapper


class GetSalesLeadsUseCase:


    def __init__(self, repository):
        self.repository = repository


    def execute(
        self,
        scope: str,
        user
    ):

        if scope == "my":

            leads = self.repository.find_my_leads(
                user.id
            )


        elif scope == "unassigned":

            leads = self.repository.find_unassigned_leads()


        else:
            raise ValueError(
                "Scope invalide"
            )


        return [
            LeadMapper.to_response(lead)
            for lead in leads
        ]