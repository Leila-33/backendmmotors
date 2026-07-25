from dataclasses import dataclass
from modules.applications.domain.enums import OptionUsageType




@dataclass
class ApplicationOption:
    id: str
    application_id: str
    option_id: str