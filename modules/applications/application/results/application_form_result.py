from dataclasses import dataclass
from modules.applications.domain.entities.application import Application

@dataclass
class ApplicationFormResult:
    application: Application
    is_new: bool