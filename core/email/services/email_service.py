from abc import ABC, abstractmethod

class EmailService(ABC):

    @abstractmethod
    def send(
        self,
        to: str,
        subject: str,
        body: str,
    ) -> None:
        pass

    @abstractmethod
    def send_verification_email(
        self,
        email: str,
        token: str,
    ) -> None:
        pass

    @abstractmethod
    def send_quote_email(
        self,
        quote,
        customer,
        vehicle,
        activation_token: str | None = None,
    ) -> None:
        pass