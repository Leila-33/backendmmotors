from modules.applications.domain.exceptions import CannotRestoreApplication
from modules.applications.domain.enums import ApplicationStatus

class RestoreApplicationPolicy:

    @staticmethod
    def validate(
        application
    ):

        if application.status != ApplicationStatus.CANCELLED:
            raise CannotRestoreApplication(
                "Le dossier n'est pas annulé."
            )

        if not application.previous_status:
            raise CannotRestoreApplication(
                "Aucun statut précédent."
            )

        if application.previous_status in (
            ApplicationStatus.PAID,
            ApplicationStatus.COMPLETED,
        ):
            raise CannotRestoreApplication(
                "Ce statut ne peut pas être restauré."
            )