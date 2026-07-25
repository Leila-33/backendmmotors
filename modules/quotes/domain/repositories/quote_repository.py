from abc import ABC, abstractmethod
from modules.quotes.domain.entities.quote import Quote

class QuoteRepository(ABC):

    @abstractmethod
    def save(self, quote):
        pass

    @abstractmethod
    def update(self, quote):
        pass

    @abstractmethod
    def find_by_id(self, quote_id):
        pass

    @abstractmethod
    def find_by_lead(self, lead_id):
        pass

    @abstractmethod
    def find_active_by_lead(self, lead_id):
        pass

    @abstractmethod
    def find_by_sales_agent(self, sales_agent_id):
        pass
    
    @abstractmethod
    def find_by_customer(self, customer_id: str):
        pass


    @abstractmethod
    def count_action_required_by_customer(
    self,
    user_id: str,
): 
        pass
    
    @abstractmethod
    def has_active_quote(
    self,
    lead_id: str,
):
        pass

    @abstractmethod
    def delete(
    self,
    quote_id: str,
):  
        pass

    @abstractmethod
    def has_any_quote(
    self,
    lead_id: str,
) -> bool:
        pass
