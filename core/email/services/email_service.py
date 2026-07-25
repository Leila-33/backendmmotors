from abc import ABC, abstractmethod


class EmailService(ABC):

    @abstractmethod
    def send(self, to: str, subject: str, body: str):
        pass
    
    def send_verification_email(self, email: str, token: str):
        raise NotImplementedError