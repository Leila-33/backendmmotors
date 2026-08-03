from abc import ABC, abstractmethod
from modules.financing.domain.entities.installment import (
    InstallmentPayment
)


class InstallmentRepository(ABC):

    # =====================================================
    # SAVE
    # =====================================================

    @abstractmethod
    def save(
        self,
        installment: InstallmentPayment
    ) -> InstallmentPayment:
        pass

    # =====================================================
    # SAVE MANY
    # =====================================================

    @abstractmethod
    def save_all(
        self,
        installments: list[InstallmentPayment]
    ) -> list[InstallmentPayment]:
        pass

    # =====================================================
    # FIND BY ID
    # =====================================================

    @abstractmethod
    def find_by_id(
        self,
        installment_id: str
    ) -> InstallmentPayment | None:
        pass

    # =====================================================
    # FIND BY STRIPE INVOICE
    # =====================================================

    @abstractmethod
    def find_by_stripe_invoice_id(
        self,
        stripe_invoice_id: str
    ) -> InstallmentPayment | None:
        pass

    # =====================================================
    # FIND NEXT UNPAID
    # =====================================================

    @abstractmethod
    def find_next_unpaid(
        self,
        contract_id: str
    ) -> InstallmentPayment | None:
        pass

    # =====================================================
    # FIND ALL BY CONTRACT
    # =====================================================

    @abstractmethod
    def find_all_by_contract_id(
        self,
        contract_id: str
    ) -> list[InstallmentPayment]:
        pass

    # =====================================================
    # COUNT
    # =====================================================

    @abstractmethod
    def count_by_contract_id(
        self,
        contract_id: str
    ) -> int:
        pass

    # =====================================================
    # UPDATE
    # =====================================================

    @abstractmethod
    def update(
        self,
        installment: InstallmentPayment
    ) -> InstallmentPayment:
        pass