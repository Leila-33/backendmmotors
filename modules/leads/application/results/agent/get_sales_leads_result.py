# modules/leads/application/results/get_sales_leads_result.py

from dataclasses import dataclass

from modules.leads.domain.entities.lead import Lead


@dataclass
class GetSalesLeadsResult:
    leads: list[Lead]