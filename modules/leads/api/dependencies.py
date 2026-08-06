from fastapi import Depends

from modules.leads.application.use_cases.create_lead import CreateLeadUseCase
from modules.leads.application.use_cases.agent.get_sales_leads import GetSalesLeadsUseCase
from modules.leads.application.use_cases.agent.assign_lead import AssignLeadUseCase
from modules.leads.application.use_cases.agent.get_lead_detail import GetLeadDetailUseCase
from modules.leads.application.use_cases.agent.mark_lead_contacted import MarkLeadContactedUseCase
from modules.leads.application.use_cases.agent.delete_lead import DeleteLeadUseCase
from modules.leads.domain.repositories.lead_repository import LeadRepository
from modules.quotes.domain.repositories.quote_repository import QuoteRepository
from modules.applications.api.dependencies import get_event_service

from modules.dependencies.dependencies import (
    get_lead_repository,
    get_lead_authorization,
    get_quote_repository,

)
from core.database.dependencies import (
    get_unit_of_work,
)

def get_create_lead_use_case(

    lead_repository = Depends(
        get_lead_repository
    ),
    event_service=Depends(get_event_service),
    unit_of_work = Depends(get_unit_of_work)
):

    return CreateLeadUseCase(

        lead_repository=lead_repository,
        event_service=event_service,
        unit_of_work = unit_of_work
    )



def get_sales_leads_usecase(
    repository: LeadRepository = Depends(get_lead_repository)
):
    return GetSalesLeadsUseCase(repository)


def get_assign_lead_usecase(
    lead_repository=Depends(get_lead_repository),
    event_service=Depends(get_event_service),
    unit_of_work = Depends(get_unit_of_work)

):

    return AssignLeadUseCase(
        lead_repository=lead_repository,
        event_service=event_service,
        unit_of_work = unit_of_work
    )

def get_lead_detail_usecase(
    lead_repository: LeadRepository = Depends(get_lead_repository),
    quote_repository: QuoteRepository = Depends(get_quote_repository)
):
    return GetLeadDetailUseCase(
        lead_repository = lead_repository,
        quote_repository = quote_repository)



def get_mark_lead_contacted_usecase(
    lead_repository=Depends(get_lead_repository),
    authorization=Depends(get_lead_authorization),
    event_service=Depends(get_event_service),
    unit_of_work = Depends(get_unit_of_work)

):

    return MarkLeadContactedUseCase(
        lead_repository=lead_repository,
        authorization=authorization,
        event_service=event_service,
        unit_of_work = unit_of_work
    )

def get_delete_lead_usecase(
    quote_repository = Depends(
        get_quote_repository
    ),

    lead_repository = Depends(
        get_lead_repository
    ),

    authorization = Depends(
        get_lead_authorization
    ),
    event_service=Depends(get_event_service),
    unit_of_work = Depends(get_unit_of_work)

):

    return DeleteLeadUseCase(

        quote_repository=quote_repository,

        lead_repository=lead_repository,

        lead_authorization=authorization,
        event_service=event_service,
        unit_of_work = unit_of_work
    )