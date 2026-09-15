from dataclasses import dataclass
from modules.applications.domain.enums import ViewMode
from modules.applications.domain.enums import (
    ApplicationStatus,
    ApplicationType
)

@dataclass
class GetApplicationsDTO:
    page: int
    limit: int
    search: str | None = None
    status: ApplicationStatus | None = None
    application_type: ApplicationType | None = None
    sort: str = "created_at_desc"
    view_mode: ViewMode = ViewMode.ACTIVE
