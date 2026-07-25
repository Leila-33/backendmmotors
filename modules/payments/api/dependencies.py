from fastapi import Depends

from core.database.dependencies import get_db

# =========================
# CORE DEPENDENCIES
# =========================
from modules.dependencies.dependencies import (
    get_payment_repository,
    get_stripe_service,
    get_application_repository,
    get_event_repository,
)

# =========================
# USE CASES - PAYMENTS
# =========================
from modules.payments.application.use_cases.create_checkout_session import CreateCheckoutSessionUseCase
from modules.payments.application.use_cases.handle_payment_success import HandlePaymentSuccessUseCase
from modules.payments.application.use_cases.create_subscription import CreateSubscriptionUseCase
from modules.payments.application.use_cases.handle_subscription_payment import HandleSubscriptionPaymentUseCase

# =========================
# FINANCING
# =========================
from modules.financing.application.use_cases.create_financing_contract import CreateFinancingContractUseCase
from modules.financing.application.use_cases.create_installments import CreateInstallmentsUseCase

# =========================
# WARRANTIES
# =========================
from modules.warranties.application.use_cases.admin.activate_vehicle_warranty import ActivateVehicleWarranty

# =========================
# REPOSITORIES (SQL)
# =========================
from modules.payments.infrastructure.repositories.payment_repository_sql import PaymentRepositorySQL
from modules.applications.infrastructure.repositories.application_repository_sql import ApplicationRepositorySQL
from modules.applications.infrastructure.repositories.event_repository_sql import EventRepositorySQL
from modules.financing.infrastructure.repositories.financing_contract_repository_sql import FinancingContractRepositorySQL
from modules.financing.infrastructure.repositories.installment_repository_sql import InstallmentRepositorySQL
from modules.warranties.infrastructure.repositories.vehicle_warranty_repository_sql import VehicleWarrantyRepositorySQL
from modules.warranties.infrastructure.repositories.warranty_plan_repository_sql import WarrantyPlanRepositorySQL
from modules.vehicles.infrastructure.repositories.vehicle_repository_sql import VehicleRepositorySQL


def get_create_checkout_usecase(
    repo=Depends(get_payment_repository),
    stripe_service=Depends(get_stripe_service),
    application_repository=Depends(get_application_repository),
    event_repository=Depends(get_event_repository)
):
    return CreateCheckoutSessionUseCase(
        payment_repository=repo,
        stripe_service=stripe_service,
        application_repository=application_repository,
        event_repository=event_repository
    )

def get_handle_payment_success_usecase(
    db=Depends(get_db)
):
    # =========================
    # REPOSITORIES
    # =========================
    payment_repository = PaymentRepositorySQL(db)
    vehicle_repository = VehicleRepositorySQL(db)
    application_repository = ApplicationRepositorySQL(db)
    warranty_repository = VehicleWarrantyRepositorySQL(db)
    financing_contract_repository = FinancingContractRepositorySQL(db)
    installment_repository = InstallmentRepositorySQL(db)
    event_repository = EventRepositorySQL(db)

    # =========================
    # SERVICES
    # =========================
    stripe_service = get_stripe_service()

    # =========================
    # USE CASES
    # =========================
    create_financing_contract_uc = CreateFinancingContractUseCase(
        application_repository=application_repository,
        financing_contract_repository=financing_contract_repository,
        event_repository=event_repository
    )

    create_subscription_uc = CreateSubscriptionUseCase(
        stripe_service=stripe_service,
        financing_contract_repository=financing_contract_repository,
        event_repository=event_repository
    )

    create_installments_uc = CreateInstallmentsUseCase(
        financing_contract_repository=financing_contract_repository,
        installment_repository=installment_repository
    )

    activate_vehicle_warranty_uc = ActivateVehicleWarranty(
        warranty_plan_repo=WarrantyPlanRepositorySQL(db)
    )

    # =========================
    # MAIN USE CASE
    # =========================
    return HandlePaymentSuccessUseCase(
        payment_repository=payment_repository,
        vehicle_repository=vehicle_repository,
        application_repository=application_repository,
        warranty_repository=warranty_repository,
        event_repository=event_repository,
        activate_vehicle_warranty_uc=activate_vehicle_warranty_uc,
        create_financing_contract_uc=create_financing_contract_uc,
        create_subscription_uc=create_subscription_uc,
        create_installments_uc=create_installments_uc
    )




def get_handle_subscription_payment_usecase(
    db=Depends(get_db)
):
    financing_contract_repository = FinancingContractRepositorySQL(db)
    installment_repository = InstallmentRepositorySQL(db)
    event_repository = EventRepositorySQL(db)
    application_repository = ApplicationRepositorySQL(db)

    return HandleSubscriptionPaymentUseCase(
        db=db,
        installment_repository=installment_repository,
        financing_contract_repository=financing_contract_repository,
        event_repository=event_repository,
        application_repository=application_repository
    )