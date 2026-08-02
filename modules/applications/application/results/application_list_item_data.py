from dataclasses import dataclass
from modules.applications.domain.entities.application import Application

@dataclass
class ApplicationListItemData:

    application: Application

    can_cancel: bool

    can_restore_cancelled: bool = False

    can_archive: bool = False

    can_delete: bool = False