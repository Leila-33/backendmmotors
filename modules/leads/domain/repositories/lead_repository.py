from abc import ABC, abstractmethod

from modules.leads.domain.entities.lead import Lead


class LeadRepository(ABC):

    # =====================================
    # CREATE
    # =====================================

    @abstractmethod
    def save(
        self,
        lead: Lead,
    ) -> None:
        pass

    # =====================================
    # UPDATE
    # =====================================

    @abstractmethod
    def update(
        self,
        lead: Lead,
    ) -> None:
        pass

    # =====================================
    # FIND BY ID
    # =====================================

    @abstractmethod
    def find_by_id(
        self,
        lead_id: str,
    ) -> Lead | None:
        pass

    # =====================================
    # FIND BY ID WITH DETAILS
    # =====================================

    @abstractmethod
    def get_by_id_with_details(
        self,
        lead_id: str,
    ) -> Lead | None:
        pass

    # =====================================
    # AGENT - MY LEADS
    # =====================================

    @abstractmethod
    def find_my_leads(
        self,
        agent_id: str,
    ) -> list[Lead]:
        pass

    # =====================================
    # AGENT - UNASSIGNED LEADS
    # =====================================

    @abstractmethod
    def find_unassigned_leads(
        self,
    ) -> list[Lead]:
        pass

    # =====================================
    # ACTIVE LEAD
    # =====================================

    @abstractmethod
    def find_active_by_user_or_email_and_vehicle(
        self,
        user_id: str | None,
        email: str,
        vehicle_id: str,
    ) -> Lead | None:
        pass

    # =====================================
    # ACTIVE LEAD - USER + VEHICLE
    # =====================================

    @abstractmethod
    def find_active_by_user_and_vehicle(
        self,
        user_id: str,
        vehicle_id: str,
    ) -> Lead | None:
        pass

    # =====================================
    # ATTACH USER
    # =====================================

    @abstractmethod
    def attach_user(
        self,
        lead_id: str,
        user_id: str,
    ) -> None:
        pass

    # =====================================
    # DELETE
    # =====================================

    @abstractmethod
    def delete(
        self,
        lead_id: str,
    ) -> None:
        pass