from modules.applications.domain.exceptions import CannotSubmitApplication
from modules.applications.domain.enums import ApplicationStatus

class SubmitApplicationPolicy:

    @staticmethod
    def validate(application):

        if application.is_archived:
            raise CannotSubmitApplication(
    "Le dossier est archivé."
)

        if application.deleted_at:
            raise CannotSubmitApplication(
    "Le dossier est supprimé."
)

        if application.status != ApplicationStatus.DRAFT:
            raise CannotSubmitApplication()