from dataclasses import dataclass
from modules.applications.domain.enums import ViewMode


@dataclass
class GetApplicationsDTO:
    page: int
    limit: int
    search: str | None = None
    status: str | None = None
    application_type: str | None = None
    sort: str = "created_at_desc"
    view_mode: ViewMode = ViewMode.ACTIVE
