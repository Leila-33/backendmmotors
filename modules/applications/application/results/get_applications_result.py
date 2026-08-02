from dataclasses import dataclass
from modules.applications.application.results.application_list_item_data import ApplicationListItemData

@dataclass
class GetApplicationsResult:

    items: list[ApplicationListItemData]
    page: int
    limit: int
    total: int
    pages: int