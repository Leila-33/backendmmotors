from modules.applications.domain.exceptions import (
    CannotDeleteApplication,
    ApplicationAlreadyDeleted
)
from modules.applications.domain.enums import ApplicationStatus

class SoftDeleteApplicationPolicy:

    @staticmethod
    def can_delete(
        application,
    ) -> bool:

        try:

            SoftDeleteApplicationPolicy.validate(
                application
            )

            return True

        except CannotDeleteApplication:
            return False

        except ApplicationAlreadyDeleted:
            return False


    @staticmethod
    def validate(
        application,
    ) -> None:


        # =========================
        # ALREADY DELETED
        # =========================
        if application.deleted_at:
            raise ApplicationAlreadyDeleted()


        # =========================
        # ONLY FINAL STATES
        # =========================
        if application.status not in (
            ApplicationStatus.CANCELLED,
            ApplicationStatus.COMPLETED,
            ApplicationStatus.REJECTED,
        ):
            raise CannotDeleteApplication(
                "Le dossier ne peut être supprimé que lorsqu'il est terminé."
            )