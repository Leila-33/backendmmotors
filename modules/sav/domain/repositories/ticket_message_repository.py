from abc import ABC, abstractmethod


class TicketMessageRepository(ABC):

    @abstractmethod
    def get_by_ticket(self, ticket_id: str):
        pass

    @abstractmethod
    def create(self, message):
        pass