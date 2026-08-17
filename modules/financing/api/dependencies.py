from fastapi import Depends

# ============================================================
# USE CASES
# ============================================================

from modules.financing.application.use_cases.estimate_trade_in import (
    EstimateTradeInUseCase,
)

from modules.financing.application.use_cases.create_installments import (
    CreateInstallmentsUseCase,
)

from modules.financing.application.use_cases.create_financing_contract import (
    CreateFinancingContractUseCase,
)


# ============================================================
# REPOSITORIES
# ============================================================

from modules.dependencies.dependencies import (
    get_application_repository,
    get_financing_contract_repository,
    get_installment_repository,
    get_event_service,
)


# ============================================================
# DOMAIN SERVICES
# ============================================================

from modules.financing.domain.services.trade_in_service import (
    TradeInService,
)

from modules.financing.domain.services.financing_service import (
    FinancingService,
)


# ============================================================
# SERVICES
# ============================================================

def get_trade_in_service() -> TradeInService:
    return TradeInService()


def get_financing_service() -> FinancingService:
    return FinancingService()


# ============================================================
# USE CASE : ESTIMATE TRADE IN
# ============================================================

def get_estimate_trade_in_usecase(
    service: TradeInService = Depends(
        get_trade_in_service
    ),
) -> EstimateTradeInUseCase:

    return EstimateTradeInUseCase(
        trade_in_estimation_service=service,
    )


# ============================================================
# USE CASE : CREATE FINANCING CONTRACT
# ============================================================

def get_create_financing_contract_usecase(
    application_repository=Depends(
        get_application_repository
    ),
    financing_contract_repository=Depends(
        get_financing_contract_repository
    ),
    event_service=Depends(
        get_event_service
    ),
) -> CreateFinancingContractUseCase:

    return CreateFinancingContractUseCase(
        application_repository=application_repository,
        financing_contract_repository=(
            financing_contract_repository
        ),
        event_service=event_service,
    )


# ============================================================
# USE CASE : CREATE INSTALLMENTS
# ============================================================

def get_create_installments_usecase(
    financing_contract_repository=Depends(
        get_financing_contract_repository
    ),
    installment_repository=Depends(
        get_installment_repository
    ),
) -> CreateInstallmentsUseCase:

    return CreateInstallmentsUseCase(
        financing_contract_repository=(
            financing_contract_repository
        ),
        installment_repository=installment_repository,
    )