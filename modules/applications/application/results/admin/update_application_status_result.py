from dataclasses import dataclass
from modules.applications.domain.enums import (
    ApplicationStatus
)

@dataclass
class UpdateApplicationStatusResult:
    id: str
    status: ApplicationStatus