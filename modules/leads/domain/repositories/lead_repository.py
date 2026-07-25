from abc import ABC, abstractmethod

from modules.leads.domain.entities.lead import Lead
from modules.leads.infrastructure.db.lead_model import LeadModel

class LeadRepository(ABC):

    @abstractmethod
    def save(self, lead: Lead) -> None:
        """
        Persist a new lead.
        """
        pass

    @abstractmethod
    def find_by_id(self, lead_id: str) -> Lead | None:
        """
        Retrieve a lead by its identifier.
        """
        pass
    
    @abstractmethod
    def get_by_id_with_details(self, lead_id: str) -> LeadModel | None:
        pass

    @abstractmethod
    def find_my_leads(self, agent_id: str):
        pass


    @abstractmethod
    def find_unassigned_leads(self):
        pass

    @abstractmethod
    def find_active_by_user_and_vehicle(
    self,
    user_id: str,
    vehicle_id: str,
):
        pass


    @abstractmethod
    def find_active_by_user_or_email_and_vehicle(
    self,
    user_id: str,
    vehicle_id: str,
):
        pass
    
    @abstractmethod
    def attach_user(
        self,
        lead_id: str,
        user_id: str,
    ):
        pass
    
    @abstractmethod
    def delete(
    self,
    lead_id: str,
):
        pass
