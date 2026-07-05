from abc import ABC, abstractmethod
from typing import List

from modules.financing.domain.entities.installment import (
    InstallmentPayment
)


class InstallmentRepository(ABC):

    @abstractmethod
    def save(self, installment: InstallmentPayment):
        pass

    @abstractmethod
    def save_all(self, installments: List[InstallmentPayment]):
        pass

    @abstractmethod
    def get_by_id(self, installment_id: str):
        pass

    @abstractmethod
    def find_next_pending(self, contract_id: str):
        pass

    @abstractmethod
    def find_by_subscription_id(self, subscription_id: str):
        pass

    @abstractmethod
    def count_by_contract_id(self, contract_id: str) -> int:
        pass

    @abstractmethod
    def commit(self):
        pass