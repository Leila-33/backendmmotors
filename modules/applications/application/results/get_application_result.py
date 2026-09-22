from dataclasses import dataclass
from modules.applications.domain.entities.application import Application

@dataclass
class GetApplicationResult:

    application: Application
    payment_status: str | None