from fastapi import Depends
# =========================
# DEPENDENCIES
# =========================
from modules.dependencies.dependencies import (
    get_payment_repository,
    get_stripe_service,
    get_application_repository,
    get_event_repository,
    get_financing_contract_repository,
    get_installment_repository,
    get_vehicle_repository,
    get_vehicle_warranty_repository
    
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
from modules.payments.application.use_cases.create_subscription import CreateSubscriptionUseCase
from modules.payments.application.use_cases.handle_subscription_payment import HandleSubscriptionPaymentUseCase
from modules.payments.application.use_cases.handle_invoice_created import (
    HandleInvoiceCreatedUseCase
)


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

    event_repository=Depends(
        get_event_repository
    ),

    uow=Depends(
        get_unit_of_work
    ),
):

    return CreateCheckoutSessionUseCase(
        payment_repository=payment_repository,
        stripe_service=stripe_service,
        application_repository=application_repository,
        event_repository=event_repository,
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

    event_repository=Depends(
        get_event_repository
    ),
    uow=Depends(
        get_unit_of_work
    ),

):

    return CreateSubscriptionUseCase(
        stripe_service=stripe_service,
        financing_contract_repository=(
            financing_contract_repository
        ),
        event_repository=event_repository,
        uow=uow,
    )

# =====================================================
# HANDLE PAYMENT SUCCESS
# =====================================================

def get_handle_payment_success_usecase(

    payment_repository=Depends(
        get_payment_repository
    ),

    vehicle_repository=Depends(
        get_vehicle_repository
    ),

    application_repository=Depends(
        get_application_repository
    ),

    warranty_repository=Depends(
        get_vehicle_warranty_repository
    ),

    event_repository=Depends(
        get_event_repository
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

    uow=Depends(
        get_unit_of_work
    ),
):

    return HandlePaymentSuccessUseCase(
        payment_repository=payment_repository,
        vehicle_repository=vehicle_repository,
        application_repository=application_repository,
        warranty_repository=warranty_repository,
        event_repository=event_repository,
        activate_vehicle_warranty_uc=activate_vehicle_warranty_uc,
        create_financing_contract_uc=create_financing_contract_uc,
        create_subscription_uc=create_subscription_uc,
        create_installments_uc=create_installments_uc,
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

    event_repository=Depends(
        get_event_repository
    ),

    uow=Depends(
        get_unit_of_work
    ),
):

    return HandleSubscriptionPaymentUseCase(
        installment_repository=installment_repository,
        financing_contract_repository=financing_contract_repository,
        application_repository=application_repository,
        event_repository=event_repository,
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