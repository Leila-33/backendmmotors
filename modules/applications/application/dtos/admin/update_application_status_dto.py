from dataclasses import dataclass
from typing import Optional
from modules.applications.domain.enums import (
    ApplicationStatus
)

@dataclass(frozen=True)
class UpdateApplicationStatusDTO:
    application_id: str
    status: ApplicationStatus
    reason: Optional[str] = None
