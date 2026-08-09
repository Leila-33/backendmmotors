from fastapi import Depends
# =========================
# DEPENDENCIES
# =========================
from modules.dependencies.dependencies import (
    get_payment_repository,
    get_application_repository,
    get_financing_contract_repository,
    get_installment_repository,
    get_vehicle_repository,
    get_event_service,
    get_lead_repository
)
from modules.financing.api.dependencies import (
    get_create_financing_contract_usecase,
    get_create_installments_usecase
)
from modules.warranties.api.dependencies import get_activate_vehicle_warranty_usecase

# =========================
# CORE
# =========================
from core.database.dependencies import (
    get_unit_of_work
)

# =========================
# USE CASES - PAYMENTS
# =========================
from modules.payments.application.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from modules.payments.application.use_cases.handle_payment_success import HandlePaymentSuccessUseCase
from modules.payments.application.use_cases.complete_rental_payment import CompleteRentalPaymentUseCase
from modules.payments.application.use_cases.complete_sale_payment import CompleteSalePaymentUseCase
from modules.payments.application.use_cases.create_subscription import CreateSubscriptionUseCase
from modules.payments.application.use_cases.handle_subscription_payment import HandleSubscriptionPaymentUseCase
from modules.payments.application.use_cases.handle_invoice_created import (
    HandleInvoiceCreatedUseCase
)


# =========================
# SERVICES
# =========================
from modules.payments.infrastructure.services.stripe_service import (
    StripeService,
)


def get_stripe_service():
    return StripeService()

# =====================================================
# CREATE CHECKOUT SESSION
# =====================================================

def get_create_checkout_session_usecase(

    payment_repository=Depends(
        get_payment_repository
    ),

    stripe_service=Depends(
        get_stripe_service
    ),

    application_repository=Depends(
        get_application_repository
    ),

    event_service=Depends(get_event_service),
    uow=Depends(
        get_unit_of_work
    ),
):

    return CreateCheckoutSessionUseCase(
        payment_repository=payment_repository,
        stripe_service=stripe_service,
        application_repository=application_repository,
        event_service=event_service,
        uow=uow,
    )

# =====================================================
# CREATE SUBSCRIPTION
# =====================================================

def get_create_subscription_usecase(

    stripe_service=Depends(
        get_stripe_service
    ),

    financing_contract_repository=Depends(
        get_financing_contract_repository
    ),

    event_service=Depends(get_event_service)

):

    return CreateSubscriptionUseCase(
        stripe_service=stripe_service,
        financing_contract_repository=(
            financing_contract_repository
        ),
        event_service=event_service,
    )

# =====================================================
# GET COMPLETE SALE PAYMENT
# =====================================================
def get_complete_sale_payment_usecase(

    vehicle_repository=Depends(
        get_vehicle_repository
    ),

    application_repository=Depends(
        get_application_repository
    ),

    lead_repository=Depends(
        get_lead_repository
    ),

    event_service=Depends(
        get_event_service
    ),

    activate_vehicle_warranty_uc=Depends(
        get_activate_vehicle_warranty_usecase
    ),

    create_financing_contract_uc=Depends(
        get_create_financing_contract_usecase
    ),

    create_subscription_uc=Depends(
        get_create_subscription_usecase
    ),

    create_installments_uc=Depends(
        get_create_installments_usecase
    ),

):

    return CompleteSalePaymentUseCase(

        vehicle_repository=vehicle_repository,

        application_repository=application_repository,

        lead_repository=lead_repository,

        event_service=event_service,

        activate_vehicle_warranty_uc=(
            activate_vehicle_warranty_uc
        ),

        create_financing_contract_uc=(
            create_financing_contract_uc
        ),

        create_subscription_uc=(
            create_subscription_uc
        ),

        create_installments_uc=(
            create_installments_uc
        ),
    )

# =====================================================
# GET RENTAL SALE PAYMENT
# =====================================================

def get_complete_rental_payment_usecase(

    vehicle_repository=Depends(
        get_vehicle_repository
    ),

    application_repository=Depends(
        get_application_repository
    ),

    event_service=Depends(
        get_event_service
    ),

):

    return CompleteRentalPaymentUseCase(

        vehicle_repository=vehicle_repository,

        application_repository=application_repository,

        event_service=event_service,

    )

# =====================================================
# HANDLE PAYMENT SUCCESS
# =====================================================
def get_handle_payment_success_usecase(

    payment_repository=Depends(
        get_payment_repository
    ),

    application_repository=Depends(
        get_application_repository
    ),

    complete_sale_payment_uc=Depends(
        get_complete_sale_payment_usecase
    ),

    complete_rental_payment_uc=Depends(
        get_complete_rental_payment_usecase
    ),

    event_service=Depends(
        get_event_service
    ),

    uow=Depends(
        get_unit_of_work
    ),

):

    return HandlePaymentSuccessUseCase(

        payment_repository=payment_repository,

        application_repository=application_repository,

        complete_sale_payment_uc=(
            complete_sale_payment_uc
        ),

        complete_rental_payment_uc=(
            complete_rental_payment_uc
        ),

        event_service=event_service,

        uow=uow,
    )

# =====================================================
# HANDLE SUBSCRIPTION PAYMENT
# =====================================================

def get_handle_subscription_payment_usecase(

    installment_repository=Depends(
        get_installment_repository
    ),

    financing_contract_repository=Depends(
        get_financing_contract_repository
    ),

    application_repository=Depends(
        get_application_repository
    ),

    event_service=Depends(get_event_service),

    uow=Depends(
        get_unit_of_work
    ),
):

    return HandleSubscriptionPaymentUseCase(
        installment_repository=installment_repository,
        financing_contract_repository=financing_contract_repository,
        application_repository=application_repository,
        event_service=event_service,
        uow=uow,
    )


# =====================================================
# HANDLE INVOICE CREATED
# =====================================================

def get_handle_invoice_created_usecase(

    financing_contract_repository=Depends(
        get_financing_contract_repository
    ),

    installment_repository=Depends(
        get_installment_repository
    ),

    uow=Depends(
        get_unit_of_work
    ),
):

    return HandleInvoiceCreatedUseCase(
        financing_contract_repository=(
            financing_contract_repository
        ),
        installment_repository=(
            installment_repository
        ),
        uow=uow,
    )