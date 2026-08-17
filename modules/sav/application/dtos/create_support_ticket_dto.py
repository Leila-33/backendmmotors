from dataclasses import dataclass

@dataclass
class CreateSupportTicketDTO:

    subject: str
    category: str
    message: str
    priority: str
    application_id: str | None