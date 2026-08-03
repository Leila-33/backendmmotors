from abc import ABC, abstractmethod
from typing import Optional

from modules.financing.domain.entities.financing_contract import FinancingContract


class FinancingContractRepository(ABC):

    # =========================
    # SAVE
    # =========================
    @abstractmethod
    def save(
        self,
        contract: FinancingContract
    ) -> FinancingContract:
        pass

    # =========================
    # FIND BY ID
    # =========================
    @abstractmethod
    def find_by_id(
        self,
        contract_id: str
    ) -> Optional[FinancingContract]:
        pass

    # =========================
    # FIND BY APPLICATION
    # =========================
    @abstractmethod
    def find_by_application_id(
        self,
        application_id: str
    ) -> Optional[FinancingContract]:
        pass

    # =========================
    # FIND BY APPLICATION
    # =========================
    @abstractmethod
    def get_by_subscription_id(
        self,
        stripe_subscription_id: str
    ) -> Optional[FinancingContract]:
        pass


    # =========================
    # UPDATE
    # =========================
    @abstractmethod
    def update(
        self,
        contract: FinancingContract
    ) -> FinancingContract:
        pass