from typing import Optional

from sqlalchemy.orm import Session

from modules.financing.domain.repositories.financing_contract_repository import (
    FinancingContractRepository
)

from modules.financing.domain.entities.financing_contract import (
    FinancingContract
)

from modules.financing.infrastructure.db.financing_contract_model import (
    FinancingContractModel
)

from modules.financing.infrastructure.mappers.financing_contract_mapper import (
    FinancingContractMapper
)

from modules.financing.domain.exceptions import (
    FinancingContractNotFound
)


class SqlFinancingContractRepository(
    FinancingContractRepository
):

    def __init__(
        self,
        session: Session
    ):

        self.session = session


    # =====================================================
    # SAVE
    # =====================================================

    def save(
        self,
        contract: FinancingContract
    ) -> FinancingContract:


        model = (
            FinancingContractMapper
            .to_model(contract)
        )


        self.session.add(model)

        self.session.flush()


        return FinancingContractMapper.to_domain(
            model
        )


    # =====================================================
    # FIND BY ID
    # =====================================================

    def find_by_id(
        self,
        contract_id: str
    ) -> Optional[FinancingContract]:


        model = (
            self.session.query(
                FinancingContractModel
            )
            .filter(
                FinancingContractModel.id == contract_id
            )
            .first()
        )


        if not model:
            return None


        return FinancingContractMapper.to_domain(
            model
        )


    # =====================================================
    # FIND BY APPLICATION
    # =====================================================

    def find_by_application_id(
        self,
        application_id: str
    ) -> Optional[FinancingContract]:


        model = (
            self.session.query(
                FinancingContractModel
            )
            .filter(
                FinancingContractModel.application_id
                == application_id
            )
            .first()
        )


        if not model:
            return None


        return FinancingContractMapper.to_domain(
            model
        )


    # =====================================================
    # FIND BY STRIPE SUBSCRIPTION
    # =====================================================

    def get_by_subscription_id(
        self,
        stripe_subscription_id: str
    ) -> Optional[FinancingContract]:


        model = (
            self.session.query(
                FinancingContractModel
            )
            .filter(
                FinancingContractModel
                .stripe_subscription_id
                == stripe_subscription_id
            )
            .first()
        )


        if not model:
            return None


        return FinancingContractMapper.to_domain(
            model
        )


    # =====================================================
    # UPDATE
    # =====================================================

    def update(
        self,
        contract: FinancingContract
    ) -> FinancingContract:


        model = (
            self.session.query(
                FinancingContractModel
            )
            .filter(
                FinancingContractModel.id
                == contract.id
            )
            .first()
        )


        if not model:
            raise FinancingContractNotFound()


        FinancingContractMapper.update_model(
            model,
            contract
        )


        self.session.flush()


        return FinancingContractMapper.to_domain(
            model
        )