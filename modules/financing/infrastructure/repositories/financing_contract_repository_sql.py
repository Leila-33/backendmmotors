from typing import Optional

from sqlalchemy.orm import Session

from modules.financing.domain.entities.financing_contract import FinancingContract
from modules.financing.domain.repositories.financing_contract_repository import (
    FinancingContractRepository
)

from modules.financing.infrastructure.db.financing_contract_model import FinancingContractModel
from modules.core.exceptions import FinancingContractNotFound
from datetime import datetime, timezone

class FinancingContractRepositorySQL(FinancingContractRepository):

    def __init__(self, db: Session):
        self.db = db

    # =========================
    # MAPPER MODEL → ENTITY
    # =========================
    def _to_entity(
        self,
        model: FinancingContractModel
    ) -> FinancingContract:

        return FinancingContract(
            id=model.id,
            application_id=model.application_id,
            financed_amount=model.financed_amount,
            monthly_payment=model.monthly_payment,
            duration_months=model.duration_months,
            remaining_balance=model.remaining_balance,
            stripe_customer_id=model.stripe_customer_id,
            stripe_subscription_id=model.stripe_subscription_id,
            subscription_status=model.subscription_status,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    # =========================
    # MAPPER ENTITY → MODEL
    # =========================
    def _to_model(
        self,
        entity: FinancingContract
    ) -> FinancingContractModel:

        return FinancingContractModel(
            id=entity.id,
            application_id=entity.application_id,
            financed_amount=entity.financed_amount,
            monthly_payment=entity.monthly_payment,
            duration_months=entity.duration_months,
            remaining_balance=entity.remaining_balance,
            stripe_customer_id=entity.stripe_customer_id,
            stripe_subscription_id=entity.stripe_subscription_id,
            subscription_status=entity.subscription_status,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    # =========================
    # SAVE
    # =========================
    def save(
        self,
        contract: FinancingContract
    ) -> FinancingContract:

        model = self._to_model(contract)

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return self._to_entity(model)

    # =========================
    # FIND BY ID
    # =========================
    def find_by_id(
        self,
        contract_id: str
    ) -> Optional[FinancingContract]:

        model = (
            self.db.query(FinancingContractModel)
            .filter(FinancingContractModel.id == contract_id)
            .first()
        )

        if not model:
            return None

        return self._to_entity(model)

    # =========================
    # FIND BY APPLICATION
    # =========================
    def find_by_application_id(
        self,
        application_id: str
    ) -> Optional[FinancingContract]:

        model = (
            self.db.query(FinancingContractModel)
            .filter(
                FinancingContractModel.application_id
                == application_id
            )
            .first()
        )

        if not model:
            return None

        return self._to_entity(model)

    # =========================
    # UPDATE
    # =========================
    def update(
        self,
        contract: FinancingContract
    ) -> FinancingContract:

        model = (
            self.db.query(FinancingContractModel)
            .filter(FinancingContractModel.id == contract.id)
            .first()
        )

        if not model:
            raise FinancingContractNotFound

        model.financed_amount = contract.financed_amount
        model.monthly_payment = contract.monthly_payment
        model.duration_months = contract.duration_months
        model.remaining_balance = contract.remaining_balance
        model.stripe_customer_id = contract.stripe_customer_id
        model.stripe_subscription_id = contract.stripe_subscription_id
        model.subscription_status = contract.subscription_status

        self.db.commit()
        self.db.refresh(model)

        return self._to_entity(model)
    
    def get_by_subscription_id(self, subscription_id: str):
        return (
            self.db.query(FinancingContractModel)
            .filter(
                FinancingContractModel.stripe_subscription_id == subscription_id
            )
            .first()
        )
    
    def update(self, contract: FinancingContract):

        model = (
            self.db.query(FinancingContractModel)
            .filter_by(id=contract.id)
            .first()
        )

        if not model:
            return None

        model.remaining_balance = contract.remaining_balance
        model.subscription_status = contract.subscription_status
        model.stripe_customer_id = contract.stripe_customer_id
        model.stripe_subscription_id = contract.stripe_subscription_id
        model.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(model)

        return model