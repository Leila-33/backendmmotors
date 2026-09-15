from datetime import datetime, timezone
from modules.leads.domain.enums import LeadStatus
from dataclasses import dataclass, field
from modules.leads.domain.exceptions import (
    LeadAlreadyAssigned,
    CannotContactLead,
    InvalidLeadState,
    LeadCannotBeAssigned
    )

from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.auth.domain.entities.user import User

@dataclass
class Lead:

    id: str
    vehicle_id: str

    first_name: str
    last_name: str
    email: str
    phone: str
    message: str
    
    created_at: datetime = field(
        default_factory=lambda:
            datetime.now(timezone.utc)
    )

    status: LeadStatus = LeadStatus.NEW

    assigned_to: str | None = None

    user_id: str | None = None

    vehicle: Vehicle | None = None

    assigned_agent: User | None = None

    def change_status(self, status):

        self.status = status


    def assign_to(self, agent_id: str):
        
        if self.status != LeadStatus.NEW:
            raise InvalidLeadState()

        if self.assigned_to:
            raise LeadAlreadyAssigned()

        self.assigned_to = agent_id
        self.status = LeadStatus.ASSIGNED



    def mark_as_contacted(self):

        if self.status != LeadStatus.ASSIGNED:
            raise CannotContactLead()


        self.status = LeadStatus.CONTACTED
        
    def win(self):

        if self.status == LeadStatus.WON:
            return

        self.status = LeadStatus.WON

    def ensure_assignable(self):

        if self.status != LeadStatus.NEW:
            raise LeadCannotBeAssigned()