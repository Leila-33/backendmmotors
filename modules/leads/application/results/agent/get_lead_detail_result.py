# modules/leads/application/results/get_lead_detail_result.py

from dataclasses import dataclass
from modules.leads.domain.entities.lead import Lead
from modules.quotes.domain.entities.quote import Quote

@dataclass
class GetLeadDetailResult:

    lead: Lead
    quotes: list[Quote]

    can_create_quote: bool
    can_delete: bool