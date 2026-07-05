from abc import ABC, abstractmethod


class PaymentRepository(ABC):

    # =========================
    # SAVE
    # =========================
    @abstractmethod
    def save(self, payment):
        pass

    # =========================
    # UPDATE
    # =========================
    @abstractmethod
    def update(self, payment):
        pass

    # =========================
    # GET BY ID
    # =========================
    @abstractmethod
    def get_by_id(self, payment_id: str):
        pass

    # =========================
    # GET BY STRIPE SESSION
    # =========================
    @abstractmethod
    def get_by_session_id(
        self,
        stripe_session_id: str
    ):
        pass

    # =========================
    # COMMIT
    # =========================
    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def get_by_application_id(self, application_id: str):
        pass