from fastapi import Depends

# =========================
# CORE
# =========================

from core.database.dependencies import (
    get_unit_of_work,
)

from core.email.dependencies import (
    get_email_service,
)

from core.email.services.email_service import (
    EmailService,
)


# =========================
# AUTH
# =========================

from modules.auth.api.dependencies import (
    get_customer_account_service,
)

from modules.auth.application.services.customer_account_service import (
    CustomerAccountService,
)


# =========================
# LEADS
# =========================

from modules.leads.api.dependencies import (
    get_lead_authorization,
)

from modules.leads.application.services.LeadAuthorizationService import (
    LeadAuthorizationService,
)

from modules.leads.domain.repositories.lead_repository import (
    LeadRepository,
)


# =========================
# NOTIFICATIONS
# =========================

from modules.notifications.api.dependencies import (
    get_notification_service,
)

from modules.notifications.application.services.notification_service import (
    NotificationService,
)


# =========================
# APPLICATIONS
# =========================

from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository,
)


# =========================
# QUOTES
# =========================

from modules.quotes.application.use_cases.agent.create_quote import (
    CreateQuoteUseCase,
)
from modules.quotes.application.use_cases.agent.update_quote import (
    UpdateQuoteUseCase,
)
from modules.quotes.application.use_cases.agent.delete_quote import (
    DeleteQuoteUseCase,
)
from modules.quotes.application.use_cases.agent.get_quote_detail import (
    GetQuoteDetailUseCase,
)

from modules.quotes.application.use_cases.agent.send_quote import (
    SendQuoteUseCase,
)

from modules.quotes.application.use_cases.accept_quote import (
    AcceptQuoteUseCase,
)

from modules.quotes.application.use_cases.refuse_quote import (
    RefuseQuoteUseCase,
)

from modules.quotes.application.use_cases.get_customer_quote_detail import (
    GetCustomerQuoteDetailUseCase,
)

from modules.quotes.application.use_cases.get_customer_quotes import (
    GetCustomerQuotesUseCase,
)

from modules.quotes.application.use_cases.get_client_quote_action_required_count import (
    GetClientQuoteActionRequiredCountUseCase,
)

from modules.quotes.domain.repositories.quote_repository import (
    QuoteRepository,
)


# =========================
# SHARED REPOSITORIES / SERVICES
# =========================

from modules.dependencies.dependencies import (
    get_application_repository,
    get_event_repository,
    get_financing_service,
    get_lead_repository,
    get_quote_repository,
    get_quote_trade_in_repository,
    get_trade_in_service,
    get_vehicle_repository,
)

def get_create_quote_usecase(
    quote_repository = Depends(
        get_quote_repository
    ),

    quote_trade_in_repository = Depends(
        get_quote_trade_in_repository
    ),

    lead_repository = Depends(
        get_lead_repository
    ),

    vehicle_repository = Depends(
        get_vehicle_repository
    ),

    financing_service = Depends(
        get_financing_service
    ),

    trade_in_service = Depends(
        get_trade_in_service
    ),

    authorization = Depends(
        get_lead_authorization
    ),
    unit_of_work = Depends(get_unit_of_work)

):

    return CreateQuoteUseCase(

        quote_repository=quote_repository,

        quote_trade_in_repository=
            quote_trade_in_repository,

        lead_repository=lead_repository,

        vehicle_repository=vehicle_repository,

        financing_service=financing_service,

        trade_in_service=trade_in_service,

        authorization=authorization,
        unit_of_work = unit_of_work
    )

def get_update_quote_usecase(
    quote_repository = Depends(
        get_quote_repository
    ),

    quote_trade_in_repository = Depends(
        get_quote_trade_in_repository
    ),

    lead_repository = Depends(
        get_lead_repository
    ),

    vehicle_repository = Depends(
        get_vehicle_repository
    ),

    financing_service = Depends(
        get_financing_service
    ),

    trade_in_service = Depends(
        get_trade_in_service
    ),

    authorization = Depends(
        get_lead_authorization
    ),
    unit_of_work = Depends(get_unit_of_work)

):

    return UpdateQuoteUseCase(

        quote_repository=quote_repository,

        quote_trade_in_repository=
            quote_trade_in_repository,

        lead_repository=lead_repository,

        vehicle_repository=vehicle_repository,

        financing_service=financing_service,

        trade_in_service=trade_in_service,

        authorization=authorization,
        unit_of_work = unit_of_work
    )

def get_delete_quote_usecase(
    quote_repository = Depends(
        get_quote_repository
    ),

    quote_trade_in_repository = Depends(
        get_quote_trade_in_repository
    ),

    lead_repository = Depends(
        get_lead_repository
    ),

    authorization = Depends(
        get_lead_authorization
    ),
    unit_of_work = Depends(get_unit_of_work)

):

    return DeleteQuoteUseCase(

        quote_repository=quote_repository,

        quote_trade_in_repository=
            quote_trade_in_repository,

        lead_repository=lead_repository,

        authorization=authorization,
        unit_of_work = unit_of_work
    )

def get_get_quote_detail_usecase(
    quote_repository=Depends(get_quote_repository),
    authorization=Depends(get_lead_authorization),
):
    return GetQuoteDetailUseCase(
        quote_repository=quote_repository,
        authorization=authorization,
    )


def get_send_quote_usecase(

    quote_repository: QuoteRepository = Depends(
        get_quote_repository,
    ),
    lead_repository: LeadRepository = Depends(get_lead_repository),

    lead_authorization : LeadAuthorizationService = Depends(get_lead_authorization),

    customer_account_service: CustomerAccountService = Depends(
        get_customer_account_service,
    ),

    email_service: EmailService = Depends(
        get_email_service,
    ),

    notification_service: NotificationService = Depends(
        get_notification_service,
    ),
    unit_of_work = Depends(get_unit_of_work)
):

    return SendQuoteUseCase(

        quote_repository=quote_repository,
        lead_repository=lead_repository,

        lead_authorization=lead_authorization,

        customer_account_service=customer_account_service,

        email_service=email_service,

        notification_service=notification_service,
        
        unit_of_work = unit_of_work

    )


def get_customer_quotes_usecase(

    quote_repository: QuoteRepository = Depends(
        get_quote_repository,
    )

):

    return GetCustomerQuotesUseCase(
        quote_repository
    )


def get_customer_quote_detail_usecase(

    quote_repository: QuoteRepository = Depends(
        get_quote_repository,
    ),
    application_repository : ApplicationRepository = Depends(get_application_repository),


):

    return GetCustomerQuoteDetailUseCase(
        quote_repository = quote_repository,
        application_repository=application_repository

    )


def get_client_quote_action_required_count_usecase(

    quote_repository: QuoteRepository = Depends(
        get_quote_repository,
    ),

):

    return GetClientQuoteActionRequiredCountUseCase(
        quote_repository
    )


def get_accept_quote_usecase(
    quote_repository: QuoteRepository = Depends(get_quote_repository),
    application_repository : ApplicationRepository = Depends(get_application_repository),
    lead_repository : LeadRepository = Depends(get_lead_repository),
    notification_service = Depends(get_notification_service),
    email_service = Depends(get_email_service),
    event_repository = Depends(get_event_repository),
    unit_of_work = Depends(get_unit_of_work)
):
    return AcceptQuoteUseCase(
        quote_repository=quote_repository,
        application_repository=application_repository,
        lead_repository=lead_repository,
        notification_service=notification_service,
        email_service=email_service,    
        event_repository = event_repository,
        unit_of_work = unit_of_work
    )


def get_refuse_quote_usecase(
        quote_repository: QuoteRepository = Depends(
        get_quote_repository
    ),
        lead_repository : LeadRepository = Depends(get_lead_repository),
        notification_service = Depends(get_notification_service),
        unit_of_work = Depends(get_unit_of_work)

):

    return RefuseQuoteUseCase(
        quote_repository=quote_repository,
        lead_repository=lead_repository,
        notification_service=notification_service,
        unit_of_work = unit_of_work
    )