from functools import lru_cache
from fastapi import Depends
from modules.financing.application.use_cases.estimate_trade_in import (
    EstimateTradeInUseCase
)
from modules.financing.application.use_cases.create_installments import CreateInstallmentsUseCase
from modules.financing.application.use_cases.create_financing_contract import CreateFinancingContractUseCase
from modules.financing.domain.services.trade_in_service import (
    TradeInService
)
from modules.dependencies.dependencies import (
    get_application_repository,
    get_financing_contract_repository,
    get_event_repository,
    get_installment_repository,
    get_financing_contract_repository
)
# =========================
# CORE
# =========================
from core.database.dependencies import (
    get_unit_of_work
)

# =====================================================
# SERVICE
# =====================================================

@lru_cache()
def get_trade_in_estimation_service():

    return TradeInService()



# =====================================================
# USE CASE
# =====================================================

def get_estimate_trade_in_use_case(
    service: TradeInService = Depends(
        get_trade_in_estimation_service
    )
):
    return EstimateTradeInUseCase(
        trade_in_estimation_service=service
    )

# =====================================================
# CREATE FINANCING CONTRACT
# =====================================================

def get_create_financing_contract_usecase(
    application_repository=Depends(get_application_repository),
    financing_contract_repository=Depends(get_financing_contract_repository),
    event_repository=Depends(get_event_repository),
    uow=Depends(get_unit_of_work),
):
    return CreateFinancingContractUseCase(
        application_repository=application_repository,
        financing_contract_repository=financing_contract_repository,
        event_repository=event_repository,
        uow=uow,
    )

# =====================================================
# CREATE INSTALLMENTS
# =====================================================

def get_create_installments_usecase(

    financing_contract_repository=Depends(
        get_financing_contract_repository
    ),

    installment_repository=Depends(
        get_installment_repository
    ),

    uow=Depends(get_unit_of_work),


):

    return CreateInstallmentsUseCase(
        financing_contract_repository=(
            financing_contract_repository
        ),
        installment_repository=installment_repository,
        uow=uow,
    )