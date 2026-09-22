from abc import ABC, abstractmethod


from abc import ABC, abstractmethod

from modules.payments.domain.entities.payment import Payment
from modules.payments.domain.enums import PaymentStatus


class PaymentRepository(ABC):

    @abstractmethod
    def save(
        self,
        payment: Payment
    ):
        pass


    @abstractmethod
    def update(
        self,
        payment: Payment
    ):
        pass


    @abstractmethod
    def get_by_id(
        self,
        payment_id: str
    ) -> Payment | None:
        pass


    @abstractmethod
    def get_by_session_id(
        self,
        stripe_session_id: str
    ) -> Payment | None:
        pass


    @abstractmethod
    def get_by_application_and_status(
        self,
        application_id: str,
        status: PaymentStatus
    ) -> Payment | None:
        pass

    @abstractmethod
    def get_latest_by_application_id(
        self,
        application_id: str,
    ):
        pass